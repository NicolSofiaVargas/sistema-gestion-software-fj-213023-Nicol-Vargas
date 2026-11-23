# main.py
"""Simulación de al menos 10 operaciones completas para el sistema Software FJ."""

from pathlib import Path
from reservas import SistemaSoftwareFJ
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from excepciones import ErrorServicioInvalido, ErrorCalculo


def ejecutar_simulacion() -> None:
    """Ejecuta 12 operaciones completas (válidas e inválidas) sin detenerse ante errores."""
    # Limpia el log anterior antes de correr la simulación completa para tener trazabilidad clara
    ruta_log = Path(__file__).resolve().parent / "eventos_software_fj.log"
    if ruta_log.exists():
        ruta_log.unlink()

    sistema = SistemaSoftwareFJ("eventos_software_fj.log")
    sistema.logger.info("=== INICIO DE SIMULACIÓN DE OPERACIONES (SOFTWARE FJ) ===")

    # Operación 1: Registro válido de cliente 1
    sistema.logger.info("--- Operación 1: Registro válido de cliente (CLI-01) ---")
    sistema.registrar_cliente("CLI-01", "Sofía Mendoza", "sofia.mendoza@empresa.com", "3004567890", activo=True)

    # Operación 2: Registro inválido de cliente (correo mal formado)
    sistema.logger.info("--- Operación 2: Registro inválido de cliente (CLI-02) ---")
    sistema.registrar_cliente("CLI-02", "Andrés Pérez", "correo-no-valido", "3001112233", activo=True)

    # Operación 3: Registro válido de cliente 2
    sistema.logger.info("--- Operación 3: Registro válido de cliente (CLI-03) ---")
    sistema.registrar_cliente("CLI-03", "Valentina Torres", "v.torres@consultora.co", "3159988776", activo=True)

    # Operación 4: Creación correcta de 3 servicios especializados (sala, equipo, asesoría)
    sistema.logger.info("--- Operación 4: Creación correcta de servicios especializados ---")
    sala_juntas = ReservaSala("SAL-101", "Sala Ejecutiva Beta", 60.0, capacidad=12, disponible=True)
    equipo_laptop = AlquilerEquipo("EQ-201", "Laptop ingeniería i7", 20.0, stock_disponible=6, disponible=True)
    asesoria_arq = AsesoriaEspecializada("ASE-301", "Asesoría Arquitectura POO", 95.0, "Ingeniería de Software", disponible=True)
    sistema.registrar_servicio(sala_juntas)
    sistema.registrar_servicio(equipo_laptop)
    sistema.registrar_servicio(asesoria_arq)

    # Operación 5: Creación incorrecta de servicio (cálculo inconsistente por tarifa <= 0 y servicio no disponible)
    sistema.logger.info("--- Operación 5: Creación incorrecta de servicios y servicio no disponible ---")
    try:
        servicio_tarifa_mala = AlquilerEquipo("EQ-999", "Proyector 4K", -15.0, stock_disponible=2)
        sistema.registrar_servicio(servicio_tarifa_mala)
    except ErrorCalculo as exc:
        sistema.logger.error(f"Error controlado al crear servicio con tarifa inválida: {exc}")

    sala_fuera_servicio = ReservaSala("SAL-102", "Auditorio Principal", 120.0, capacidad=50, disponible=False)
    sistema.registrar_servicio(sala_fuera_servicio)

    # Operación 6: Reserva exitosa de sala (con cálculo de costo con descuento e impuesto)
    sistema.logger.info("--- Operación 6: Reserva exitosa de sala (RES-01) ---")
    sistema.crear_reserva(
        codigo_reserva="RES-01",
        codigo_cliente="CLI-01",
        codigo_servicio="SAL-101",
        duracion_horas=3,
        cantidad=8,
        descuento_pct=10.0,
        impuesto_pct=19.0,
    )
    sistema.confirmar_reserva("RES-01")

    # Operación 7: Reserva fallida por servicio no disponible (SAL-102)
    sistema.logger.info("--- Operación 7: Reserva fallida por servicio no disponible (RES-02) ---")
    sistema.crear_reserva(
        codigo_reserva="RES-02",
        codigo_cliente="CLI-01",
        codigo_servicio="SAL-102",
        duracion_horas=2,
        cantidad=10,
    )

    # Operación 8: Reserva exitosa de alquiler de equipos (RES-03)
    sistema.logger.info("--- Operación 8: Reserva exitosa de alquiler de equipos (RES-03) ---")
    sistema.crear_reserva(
        codigo_reserva="RES-03",
        codigo_cliente="CLI-03",
        codigo_servicio="EQ-201",
        duracion_horas=4,
        cantidad=3,
        descuento_pct=5.0,
        impuesto_pct=19.0,
    )
    sistema.confirmar_reserva("RES-03")
    sistema.procesar_reserva("RES-03")

    # Operación 9: Reserva fallida por parámetros inválidos (excede capacidad o duración inválida)
    sistema.logger.info("--- Operación 9: Reserva fallida por parámetros inválidos (RES-04) ---")
    sistema.crear_reserva(
        codigo_reserva="RES-04",
        codigo_cliente="CLI-03",
        codigo_servicio="SAL-101",
        duracion_horas=2,
        cantidad=25,  # Supera la capacidad de 12 personas
    )

    # Operación 10: Reserva exitosa de asesoría especializada (RES-05)
    sistema.logger.info("--- Operación 10: Reserva exitosa de asesoría especializada (RES-05) ---")
    sistema.crear_reserva(
        codigo_reserva="RES-05",
        codigo_cliente="CLI-01",
        codigo_servicio="ASE-301",
        duracion_horas=2.5,
        cantidad=1,
        impuesto_pct=19.0,
    )
    sistema.confirmar_reserva("RES-05")

    # Operación 11: Operación no permitida (intentar cancelar una reserva ya PROCESADA: RES-03)
    sistema.logger.info("--- Operación 11: Operación no permitida al cancelar RES-03 ya procesada ---")
    sistema.cancelar_reserva("RES-03", motivo="Intento tardío tras procesamiento")

    # Operación 12: Cancelación válida de una reserva confirmada (RES-01)
    sistema.logger.info("--- Operación 12: Cancelación válida de reserva confirmada (RES-01) ---")
    sistema.cancelar_reserva("RES-01", motivo="Reprogramación de reunión")

    sistema.logger.info("=== RESUMEN FINAL DEL SISTEMA (EN MEMORIA) ===")
    sistema.logger.info(f"Clientes registrados: {len(sistema.clientes)}")
    for c in sistema.clientes:
        sistema.logger.info(f"  -> {c.obtener_resumen()}")

    sistema.logger.info(f"Servicios registrados: {len(sistema.servicios)}")
    for s in sistema.servicios:
        sistema.logger.info(f"  -> {s.describir()}")

    sistema.logger.info(f"Reservas registradas: {len(sistema.reservas)}")
    for r in sistema.reservas:
        sistema.logger.info(f"  -> {r.resumir()}")

    sistema.logger.info("=== FIN DE SIMULACIÓN SIN INTERRUPCIONES ===")


if __name__ == "__main__":
    ejecutar_simulacion()