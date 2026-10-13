"""Canal endemico y generacion de alertas tempranas."""

import smtplib
import statistics
from email.message import EmailMessage

from vigisalud import config
from vigisalud.canal import clasificar_zona
from vigisalud.datos import DISTRITOS
from vigisalud.modelos import Alerta


def calcular_canal_endemico(conteos, semana_actual):
    """Calcula cuartiles historicos por distrito, enfermedad y semana."""
    canal = []
    for distrito in sorted(DISTRITOS):
        for enfermedad in sorted(config.ENFERMEDADES):
            for semana in range(1, semana_actual + 1):
                por_anio = conteos.get((distrito, enfermedad, semana), {})
                historico = [por_anio.get(anio, 0) for anio in config.ANIOS_HISTORICOS]
                q1, mediana, q3 = statistics.quantiles(historico, n=4)
                canal.append({"distrito": distrito, "enfermedad": enfermedad,
                              "semana": semana, "q1": q1, "mediana": mediana, "q3": q3,
                              "actual": por_anio.get(config.ANIO_ACTUAL, 0)})
    return canal


def detectar_alertas(canal):
    """Genera alertas cuando los casos superan el tercer cuartil."""
    return [Alerta(f["distrito"], f["enfermedad"], f["semana"], f["actual"], f["q3"], "EPIDEMIA")
            for f in canal
            if clasificar_zona(f["actual"], f["q1"], f["mediana"], f["q3"]) == "EPIDEMIA"]


def enviar_alerta_correo(alerta, destinatario):
    """Envia la alerta por correo a la oficina de epidemiologia."""
    mensaje = EmailMessage()
    mensaje["Subject"] = f"ALERTA {alerta.enfermedad} - {alerta.distrito}"
    mensaje["From"] = config.USUARIO_SMTP
    mensaje["To"] = destinatario
    mensaje.set_content(f"Semana {alerta.semana}: {alerta.casos} casos "
                        f"(limite {alerta.limite_superior}).")
    with smtplib.SMTP(config.SERVIDOR_SMTP, config.PUERTO_SMTP,
                      timeout=config.TIEMPO_ESPERA_SMTP) as servidor:
        servidor.starttls()
        servidor.login(config.USUARIO_SMTP, config.CLAVE_SMTP)
        servidor.send_message(mensaje)
