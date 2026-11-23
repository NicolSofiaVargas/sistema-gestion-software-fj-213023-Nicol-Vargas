# reservas.py
"""Clase Reserva y sistema gestor en memoria mediante listas internas para Software FJ."""

from typing import List, Optional
from entidades import Cliente
from servicios import Servicio
from excepciones import (
    ErrorBaseSoftwareFJ,
    ErrorClienteInvalido,
    ErrorServicioInvalido,
    ErrorReserva,
    ErrorCalculo,
    ErrorOperacion,
)
from registro_logs import obtener_logger


class Reserva:
    """Integra cliente, servicio, duración y estado con confirmación, cancelación y procesamiento."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "PROCESADA", "CANCELADA")

    def __init__(
        self,
        codigo_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        cantidad: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> None:
        if not isinstance(codigo_reserva, str) or not codigo_reserva.strip():
            raise ErrorReserva("El código de la reserva es obligatorio.")
        if not isinstance(cliente, Cliente):
            raise ErrorReserva("La reserva requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ErrorReserva("La reserva requiere una instancia válida de Servicio.")
        if not cliente.activo:
            raise ErrorReserva(f"El cliente '{cliente.nombre}' está inactivo y no puede realizar reservas.")

        # Valida parámetros del servicio y calcula el costo inicial
        servicio.validar_disponibilidad()
        servicio.validar_parametros(duracion_horas, cantidad)
        costo = servicio.calcular_costo(
            duracion_horas,
            cantidad=cantidad,
            descuento_pct=descuento_pct,
            impuesto_pct=impuesto_pct,
        )

        self.codigo_reserva = codigo_reserva.strip().upper()
        self.cliente = cliente
        self.servicio = servicio
        self.duracion_horas = float(duracion_horas)
        self.cantidad = int(cantidad)
        self.descuento_pct = float(descuento_pct)
        self.impuesto_pct = float(impuesto_pct)
        self.estado = "PENDIENTE"
        self.costo_total = costo

    def confirmar(self) -> None:
        """Confirma una reserva pendiente validando estado, disponibilidad y costo."""
        if self.estado == "CANCELADA":
            raise ErrorOperacion(f"No se puede confirmar la reserva '{self.codigo_reserva}' porque está cancelada.")
        if self.estado == "PROCESADA":
            raise ErrorOperacion(f"La reserva '{self.codigo_reserva}' ya fue procesada.")
        if self.estado == "CONFIRMADA":
            raise ErrorOperacion(f"La reserva '{self.codigo_reserva}' ya se encuentra confirmada.")

        try:
            self.servicio.validar_disponibilidad()
            self.costo_total = self.servicio.calcular_costo(
                self.duracion_horas,
                cantidad=self.cantidad,
                descuento_pct=self.descuento_pct,
                impuesto_pct=self.impuesto_pct,
            )
        except (ErrorServicioInvalido, ErrorCalculo) as exc:
            # Encadenamiento de excepciones: conserva la causa original
            raise ErrorReserva(f"Fallo al confirmar la reserva '{self.codigo_reserva}'.") from exc

        self.estado = "CONFIRMADA"

    def procesar(self) -> None:
        """Procesa una reserva previamente confirmada."""
        if self.estado != "CONFIRMADA":
            raise ErrorOperacion(
                f"Solo se pueden procesar reservas en estado CONFIRMADA. Estado actual de '{self.codigo_reserva}': {self.estado}."
            )
        self.estado = "PROCESADA"

    def cancelar(self, motivo: str = "Cancelación solicitada") -> None:
        """Cancela una reserva si aún no ha sido procesada ni cancelada."""
        if self.estado == "PROCESADA":
            raise ErrorOperacion(f"No se puede cancelar la reserva '{self.codigo_reserva}' porque ya fue procesada.")
        if self.estado == "CANCELADA":
            raise ErrorOperacion(f"La reserva '{self.codigo_reserva}' ya está cancelada.")

        self.estado = "CANCELADA"
        self.motivo_cancelacion = motivo.strip() if motivo else "Sin motivo especificado"

    def resumir(self) -> str:
        """Devuelve un resumen claro de la reserva."""
        return (
            f"Reserva [{self.codigo_reserva}] | Cliente: {self.cliente.nombre} ({self.cliente.codigo_id}) | "
            f"Servicio: {self.servicio.codigo} | Duración: {self.duracion_horas}h | "
            f"Cantidad: {self.cantidad} | Total: ${self.costo_total:.2f} | Estado: {self.estado}"
        )


class SistemaSoftwareFJ:
    """Gestor integral en memoria (listas internas + archivo de logs, sin base de datos)."""

    def __init__(self, nombre_log: str = "eventos_software_fj.log") -> None:
        self.logger = obtener_logger(nombre_log)
        # Listas internas en memoria (no se usa base de datos)
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []
        self.logger.info("SistemaSoftwareFJ inicializado en memoria (listas internas, sin BD).")

    def buscar_cliente(self, codigo_cliente: str) -> Optional[Cliente]:
        """Busca un cliente por código en la lista interna."""
        codigo_norm = str(codigo_cliente).strip().upper()
        for cliente in self.clientes:
            if cliente.codigo_id == codigo_norm:
                return cliente
        return None

    def buscar_servicio(self, codigo_servicio: str) -> Optional[Servicio]:
        """Busca un servicio por código en la lista interna."""
        codigo_norm = str(codigo_servicio).strip().upper()
        for servicio in self.servicios:
            if servicio.codigo == codigo_norm:
                return servicio
        return None

    def buscar_reserva(self, codigo_reserva: str) -> Optional[Reserva]:
        """Busca una reserva por código en la lista interna."""
        codigo_norm = str(codigo_reserva).strip().upper()
        for reserva in self.reservas:
            if reserva.codigo_reserva == codigo_norm:
                return reserva
        return None

    def registrar_cliente(self, codigo_id: str, nombre: str, correo: str, telefono: str, activo: bool = True) -> Optional[Cliente]:
        """Registra un cliente en la lista interna usando try/except/else/finally."""
        cliente_creado: Optional[Cliente] = None
        try:
            if self.buscar_cliente(codigo_id) is not None:
                raise ErrorClienteInvalido(f"Ya existe un cliente registrado con el código '{codigo_id}'.")
            cliente_creado = Cliente(codigo_id, nombre, correo, telefono, activo=activo)
        except ErrorClienteInvalido as exc:
            self.logger.error(f"Error al registrar cliente '{codigo_id}': {exc}")
        except Exception as exc:
            # Encadena una excepción inesperada dentro de la excepción del dominio
            error_encadenado = ErrorClienteInvalido(f"Error inesperado al crear cliente '{codigo_id}'.")
            try:
                raise error_encadenado from exc
            except ErrorClienteInvalido as chained:
                self.logger.error(f"{chained} | Causa: {chained.__cause__}")
        else:
            self.clientes.append(cliente_creado)
            self.logger.info(f"Cliente registrado con éxito: {cliente_creado.obtener_resumen()}")
        finally:
            self.logger.info(f"Intento de registro de cliente '{codigo_id}' finalizado. Total clientes: {len(self.clientes)}")
        return cliente_creado

    def registrar_servicio(self, servicio: Servicio) -> bool:
        """Agrega un servicio válido a la lista interna."""
        try:
            if not isinstance(servicio, Servicio):
                raise ErrorServicioInvalido("Solo se pueden registrar objetos de tipo Servicio.")
            if self.buscar_servicio(servicio.codigo) is not None:
                raise ErrorServicioInvalido(f"Ya existe un servicio con el código '{servicio.codigo}'.")
        except ErrorServicioInvalido as exc:
            self.logger.error(f"Error al registrar servicio: {exc}")
            return False
        else:
            self.servicios.append(servicio)
            self.logger.info(f"Servicio registrado: {servicio.describir()}")
            return True
        finally:
            self.logger.info(f"Operación de registro de servicio concluida. Total servicios: {len(self.servicios)}")

    def crear_reserva(
        self,
        codigo_reserva: str,
        codigo_cliente: str,
        codigo_servicio: str,
        duracion_horas: float,
        cantidad: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> Optional[Reserva]:
        """Crea una reserva vinculando cliente y servicio desde las listas internas."""
        reserva_nueva: Optional[Reserva] = None
        try:
            cliente = self.buscar_cliente(codigo_cliente)
            if cliente is None:
                raise ErrorClienteInvalido(f"Cliente '{codigo_cliente}' no encontrado en el sistema.")

            servicio = self.buscar_servicio(codigo_servicio)
            if servicio is None:
                raise ErrorServicioInvalido(f"Servicio '{codigo_servicio}' no encontrado en el sistema.")

            if self.buscar_reserva(codigo_reserva) is not None:
                raise ErrorReserva(f"El código de reserva '{codigo_reserva}' ya está en uso.")

            reserva_nueva = Reserva(
                codigo_reserva=codigo_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion_horas=duracion_horas,
                cantidad=cantidad,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
            )
        except (ErrorClienteInvalido, ErrorServicioInvalido, ErrorCalculo) as exc:
            # Encadenamos la causa específica dentro de ErrorReserva
            try:
                raise ErrorReserva(f"No se pudo crear la reserva '{codigo_reserva}'.") from exc
            except ErrorReserva as chained:
                self.logger.error(f"{chained} | Detalle: {chained.__cause__}")
        except ErrorReserva as exc:
            self.logger.error(f"Error de reserva '{codigo_reserva}': {exc}")
        else:
            self.reservas.append(reserva_nueva)
            self.logger.info(f"Reserva creada en estado PENDIENTE: {reserva_nueva.resumir()}")
        finally:
            self.logger.info(f"Proceso de creación de reserva '{codigo_reserva}' terminado. Total reservas: {len(self.reservas)}")
        return reserva_nueva

    def confirmar_reserva(self, codigo_reserva: str) -> bool:
        """Confirma una reserva existente."""
        try:
            reserva = self.buscar_reserva(codigo_reserva)
            if reserva is None:
                raise ErrorReserva(f"No existe la reserva '{codigo_reserva}' para confirmar.")
            reserva.confirmar()
        except (ErrorReserva, ErrorOperacion) as exc:
            self.logger.error(f"Error al confirmar '{codigo_reserva}': {exc}")
            return False
        else:
            self.logger.info(f"Reserva confirmada: {reserva.resumir()}")
            return True
        finally:
            self.logger.info(f"Revisión de confirmación para '{codigo_reserva}' completada.")

    def procesar_reserva(self, codigo_reserva: str) -> bool:
        """Procesa una reserva confirmada."""
        try:
            reserva = self.buscar_reserva(codigo_reserva)
            if reserva is None:
                raise ErrorReserva(f"No existe la reserva '{codigo_reserva}' para procesar.")
            reserva.procesar()
        except (ErrorReserva, ErrorOperacion) as exc:
            self.logger.error(f"Error al procesar '{codigo_reserva}': {exc}")
            return False
        else:
            self.logger.info(f"Reserva procesada con éxito: {reserva.resumir()}")
            return True
        finally:
            self.logger.info(f"Revisión de procesamiento para '{codigo_reserva}' completada.")

    def cancelar_reserva(self, codigo_reserva: str, motivo: str = "Cancelación por usuario") -> bool:
        """Cancela una reserva si es permitido."""
        try:
            reserva = self.buscar_reserva(codigo_reserva)
            if reserva is None:
                raise ErrorReserva(f"No existe la reserva '{codigo_reserva}' para cancelar.")
            reserva.cancelar(motivo=motivo)
        except (ErrorReserva, ErrorOperacion) as exc:
            self.logger.error(f"Error al cancelar '{codigo_reserva}': {exc}")
            return False
        else:
            self.logger.info(f"Reserva cancelada ({motivo}): {reserva.resumir()}")
            return True
        finally:
            self.logger.info(f"Revisión de cancelación para '{codigo_reserva}' completada.")