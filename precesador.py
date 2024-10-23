"""
Se modifica el archivo procesador.py para que las clases
ProcesadorAudio y ProcesadorConUmbral hereden de BaseProcesador
"""

from abc import ABCMeta, abstractmethod
from modelo.senial import *


class BaseProcesador(metaclass=ABCMeta):
    """
    Clase Abstracta Procesador
    """
    def __init__(self, senial: SenialBase):
        """
        Se inicializa con la senial que se va a procesar
        """
        self._senial_procesada = senial
        return

    @abstractmethod
    def procesar(self, senial) -> None:
        """
        Metodo abstracto que se implementara para cada tipo de procesamiento
        """
        pass

    def obtener_senial_procesada(self) -> SenialBase:
        """
        Devuelve la señal procesada
        """
        return self._senial_procesada