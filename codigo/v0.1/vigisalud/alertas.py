"""Canal endemico y generacion de alertas tempranas."""

import smtplib
import statistics
from email.message import EmailMessage

from vigisalud import config, repositorio
from vigisalud.datos import listar_distritos
from vigisalud.modelos import Alerta


def clasificar_zona(casos, q1, mediana, q3):
    """Ubica los casos observados en las zonas del canal endemico."""
    if casos <= q1:
        zona = "EXITO"
    elif casos <= mediana:
        zona = "SEGURIDAD"
    elif casos <= q3:
        zona = "ALARMA"
    else:
        zona = "EPIDEMIA"
    return zona


def calcular_canal_endemico(ruta_bd, semana_actual):
    """Calcula cuartiles historicos por distrito, enfermedad y semana."""
    canal = []
    for distrito in listar_distritos():
        for enfermedad in config.ENFERMEDADES:
            for semana in range(1, semana_actual + 1):
                por_anio = repositorio.contar_casos_por_anio(ruta_bd, distrito, enfermedad, semana)
                historico = []
                for anio in config.ANIOS_HISTORICOS:
                    historico.append(por_anio.get(anio, 0))
                q1, mediana, q3 = statistics.quantiles(historico, n=4)
                canal.append({"distrito": distrito, "enfermedad": enfermedad,
                              "semana": semana, "q1": q1, "mediana": mediana, "q3": q3,
                              "actual": por_anio.get(config.ANIO_ACTUAL, 0)})
    return canal


def detectar_alertas(canal):
    """Genera alertas cuando los casos superan el tercer cuartil."""
    alertas = []
    for fila in canal:
        zona = clasificar_zona(fila["actual"], fila["q1"], fila["mediana"], fila["q3"])
        if zona == "EPIDEMIA":
            alertas.append(Alerta(fila["distrito"], fila["enfermedad"], fila["semana"],
                                  fila["actual"], fila["q3"], zona))
    return alertas


def enviar_alerta_correo(alerta, destinatario):
    """Envia la alerta por correo a la oficina de epidemiologia."""
    mensaje = EmailMessage()
    mensaje["Subject"] = f"ALERTA {alerta.enfermedad} - {alerta.distrito}"
    mensaje["From"] = config.USUARIO_SMTP
    mensaje["To"] = destinatario
    mensaje.set_content(f"Semana {alerta.semana}: {alerta.casos} casos "
                        f"(limite {alerta.limite_superior}).")
    servidor = smtplib.SMTP(config.SERVIDOR_SMTP, config.PUERTO_SMTP)
    servidor.login(config.USUARIO_SMTP, config.CLAVE_SMTP)
    servidor.send_message(mensaje)
