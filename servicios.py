# servicios.py
"""Clase abstracta Servicio y servicios derivados de Software FJ."""

from abc import ABC, abstractmethod
from typing import overload
from excepciones import ErrorServicioInvalido, ErrorCalculo


class Servicio(ABC):
    """Clase abstracta base para los servicios de Software FJ."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        if not isinstance(codigo, str) or not codigo.strip():
            raise ErrorServicioInvalido("El código del servicio es obligatorio.")
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise ErrorServicioInvalido("El nombre del servicio debe tener al menos 3 caracteres.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ErrorCalculo("La tarifa base del servicio debe ser mayor que cero.")
        if not isinstance(disponible, bool):
            raise ErrorServicioInvalido("La disponibilidad del servicio debe ser booleana (True/False).")

        self.codigo = codigo.strip().upper()
        self.nombre = nombre.strip()
        self.tarifa_base = float(tarifa_base)
        self.disponible = disponible

    def validar_disponibilidad(self) -> None:
        """Verifica que el servicio esté disponible para reservar."""
        if not self.disponible:
            raise ErrorServicioInvalido(
                f"El servicio '{self.nombre}' ({self.codigo}) no se encuentra disponible."
            )

    @abstractmethod
    def validar_parametros(self, duracion_horas: float, cantidad: int = 1) -> None:
        """Método sobrescrito por cada servicio para validar duración y cantidad."""

    @abstractmethod
    def describir(self) -> str:
        """Método sobrescrito por cada servicio para mostrar su descripción."""

    @abstractmethod
    def _calcular_subtotal(self, duracion_horas: float, cantidad: int) -> float:
        """Calcula el subtotal base según el tipo de servicio antes de descuentos e impuestos."""

    @overload
    def calcular_costo(self, duracion_horas: float) -> float: ...

    @overload
    def calcular_costo(
        self,
        duracion_horas: float,
        cantidad: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float: ...

    def calcular_costo(
        self,
        duracion_horas: float,
        cantidad: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """Calcula el costo total soportando sobrecarga mediante parámetros opcionales."""
        self.validar_parametros(duracion_horas, cantidad)

        if not isinstance(descuento_pct, (int, float)) or descuento_pct < 0 or descuento_pct >= 100:
            raise ErrorCalculo("El porcentaje de descuento debe estar entre 0 y menor a 100.")
        if not isinstance(impuesto_pct, (int, float)) or impuesto_pct < 0 or impuesto_pct > 100:
            raise ErrorCalculo("El porcentaje de impuesto debe estar entre 0 y 100.")

        subtotal = self._calcular_subtotal(duracion_horas, cantidad)
        if subtotal <= 0:
            raise ErrorCalculo("El subtotal calculado es inconsistente (debe ser mayor a cero).")

        monto_descuento = subtotal * (float(descuento_pct) / 100.0)
        base_con_descuento = subtotal - monto_descuento
        total_final = base_con_descuento * (1.0 + float(impuesto_pct) / 100.0)

        if total_final <= 0:
            raise ErrorCalculo("El costo final calculado es inconsistente.")

        return round(total_final, 2)


class ReservaSala(Servicio):
    """Servicio derivado para reserva de salas."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        capacidad: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ErrorServicioInvalido("La capacidad de la sala debe ser un número entero mayor a cero.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion_horas: float, cantidad: int = 1) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorServicioInvalido("La duración para reservar una sala debe ser mayor a 0 horas.")
        if not isinstance(cantidad, int) or cantidad < 1 or cantidad > self.capacidad:
            raise ErrorServicioInvalido(
                f"Cantidad de asistentes ({cantidad}) no válida para la sala '{self.nombre}' (capacidad: {self.capacidad})."
            )

    def _calcular_subtotal(self, duracion_horas: float, cantidad: int) -> float:
        factor_ocupacion = 1.15 if cantidad > (self.capacidad / 2) else 1.0
        return self.tarifa_base * float(duracion_horas) * factor_ocupacion

    def describir(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[Reserva de Sala] {self.codigo} - {self.nombre} | "
            f"Capacidad: {self.capacidad} personas | Tarifa/h: ${self.tarifa_base:.2f} | {estado}"
        )


class AlquilerEquipo(Servicio):
    """Servicio derivado para alquiler de equipos."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        stock_disponible: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(stock_disponible, int) or stock_disponible <= 0:
            raise ErrorServicioInvalido("El stock del equipo debe ser un número entero mayor a cero.")
        self.stock_disponible = stock_disponible

    def validar_parametros(self, duracion_horas: float, cantidad: int = 1) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorServicioInvalido("La duración del alquiler de equipo debe ser mayor a 0 horas.")
        if not isinstance(cantidad, int) or cantidad <= 0 or cantidad > self.stock_disponible:
            raise ErrorServicioInvalido(
                f"Cantidad de equipos ({cantidad}) inválida. Stock disponible: {self.stock_disponible}."
            )

    def _calcular_subtotal(self, duracion_horas: float, cantidad: int) -> float:
        return self.tarifa_base * float(duracion_horas) * cantidad

    def describir(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[Alquiler de Equipo] {self.codigo} - {self.nombre} | "
            f"Stock: {self.stock_disponible} | Tarifa/h/equipo: ${self.tarifa_base:.2f} | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio derivado para asesorías especializadas."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        area_especialidad: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(area_especialidad, str) or len(area_especialidad.strip()) < 3:
            raise ErrorServicioInvalido("El área de especialidad de la asesoría es obligatoria.")
        self.area_especialidad = area_especialidad.strip()

    def validar_parametros(self, duracion_horas: float, cantidad: int = 1) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas < 1:
            raise ErrorServicioInvalido("Una asesoría especializada requiere al menos 1 hora.")
        if not isinstance(cantidad, int) or cantidad != 1:
            raise ErrorServicioInvalido("Para asesorías especializadas, la cantidad debe ser 1.")

    def _calcular_subtotal(self, duracion_horas: float, cantidad: int) -> float:
        return self.tarifa_base * float(duracion_horas)

    def describir(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[Asesoría Especializada] {self.codigo} - {self.nombre} "
            f"(Área: {self.area_especialidad}) | Tarifa/h: ${self.tarifa_base:.2f} | {estado}"
        )