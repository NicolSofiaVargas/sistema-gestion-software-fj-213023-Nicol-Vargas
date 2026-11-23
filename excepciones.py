# excepciones.py
"""Excepciones personalizadas para el sistema de Software FJ."""


class ErrorBaseSoftwareFJ(Exception):
    """Clase base para todas las excepciones del sistema."""


class ErrorClienteInvalido(ErrorBaseSoftwareFJ):
    """Se lanza cuando los datos de un cliente son inválidos o incompletos."""


class ErrorServicioInvalido(ErrorBaseSoftwareFJ):
    """Se lanza cuando un servicio tiene datos incorrectos o no está disponible."""


class ErrorReserva(ErrorBaseSoftwareFJ):
    """Se lanza cuando ocurre un error al crear, confirmar, procesar o cancelar una reserva."""


class ErrorCalculo(ErrorBaseSoftwareFJ):
    """Se lanza cuando hay un cálculo inconsistente o un valor numérico inválido."""


class ErrorOperacion(ErrorBaseSoftwareFJ):
    """Se lanza cuando se intenta una operación no permitida en el estado actual."""