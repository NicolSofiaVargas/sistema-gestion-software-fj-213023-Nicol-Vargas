# entidades.py
"""Clase abstracta general de entidades y clase Cliente con encapsulación y validaciones."""

from abc import ABC, abstractmethod
import re
from excepciones import ErrorClienteInvalido


class EntidadGeneral(ABC):
    """Clase abstracta que representa entidades generales del sistema."""

    def __init__(self, codigo_id: str) -> None:
        # Se valida el identificador al construir cualquier entidad general
        self._codigo_id = self._validar_codigo(codigo_id)

    @staticmethod
    def _validar_codigo(codigo: str) -> str:
        """Valida que el identificador sea un texto no vacío."""
        if not isinstance(codigo, str) or not codigo.strip():
            raise ErrorClienteInvalido("El código identificador es obligatorio y debe ser un texto.")
        return codigo.strip().upper()

    @property
    def codigo_id(self) -> str:
        """Acceso de solo lectura al código identificador."""
        return self._codigo_id

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Método abstracto que cada entidad debe implementar para describirse."""


class Cliente(EntidadGeneral):
    """Representa un cliente de Software FJ con encapsulación y validaciones estrictas."""

    def __init__(
        self,
        codigo_id: str,
        nombre: str,
        correo: str,
        telefono: str,
        activo: bool = True,
    ) -> None:
        super().__init__(codigo_id)
        # Atributos encapsulados
        self._nombre = ""
        self._correo = ""
        self._telefono = ""
        self._activo = True

        # Se usan las propiedades para aplicar las validaciones desde el inicio
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.activo = activo

    @property
    def nombre(self) -> str:
        """Obtiene el nombre del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y asigna el nombre del cliente."""
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorClienteInvalido("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        """Obtiene el correo electrónico del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida y asigna el correo electrónico del cliente."""
        patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not isinstance(valor, str) or not re.match(patron, valor.strip()):
            raise ErrorClienteInvalido("El correo electrónico del cliente no es válido.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        """Obtiene el teléfono del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida y asigna el teléfono del cliente (mínimo 7 dígitos)."""
        texto = str(valor) if valor is not None else ""
        solo_digitos = re.sub(r"[\s\-()]", "", texto)
        if not solo_digitos.isdigit() or len(solo_digitos) < 7:
            raise ErrorClienteInvalido("El teléfono del cliente debe tener al menos 7 dígitos numéricos.")
        self._telefono = solo_digitos

    @property
    def activo(self) -> bool:
        """Indica si el cliente está activo."""
        return self._activo

    @activo.setter
    def activo(self, estado: bool) -> None:
        """Valida y asigna el estado booleano del cliente."""
        if not isinstance(estado, bool):
            raise ErrorClienteInvalido("El estado del cliente debe ser un valor booleano (True o False).")
        self._activo = estado

    def obtener_resumen(self) -> str:
        """Implementación del método abstracto para mostrar la información del cliente."""
        estado_texto = "Activo" if self._activo else "Inactivo"
        return (
            f"Cliente [{self._codigo_id}] | Nombre: {self._nombre} | "
            f"Correo: {self._correo} | Teléfono: {self._telefono} | Estado: {estado_texto}"
        )