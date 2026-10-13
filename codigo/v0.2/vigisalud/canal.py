"""Reglas del canal endemico compartidas por alertas y reportes."""

ZONAS = ("EXITO", "SEGURIDAD", "ALARMA", "EPIDEMIA")


def clasificar_zona(casos, q1, mediana, q3):
    """Ubica los casos observados en las zonas del canal endemico."""
    for zona, limite in zip(ZONAS, (q1, mediana, q3)):
        if casos <= limite:
            return zona
    return ZONAS[-1]
