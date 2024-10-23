from abc import ABC, abstractmethod
from scipy.io import wavfile  # Importar la librería soundfile para leer archivos WAV

class SenialBase(ABC):
    """
    Clase abstracta que representa una señal.

    Esta clase define una interfaz común para todas las señales,
    especificando los métodos que deben implementarse en las subclases.
    """

    def __init__(self, datos: any):
        """
        Inicializa la señal con los datos.

        Args:
            datos: Los datos que representan la señal (puede ser una lista, un array de NumPy, etc.).
        """
        self.datos = datos


    @abstractmethod
    def procesar(self):
        """
        Procesa la señal.

        """
        pass

    @abstractmethod
    def graficar(self):
        """
        Grafica la señal.
        """
        pass

class SenialAudio(SenialBase):
    """
    Clase abstracta que representa una señal de audio.

    Esta clase hereda de SenialBase y agrega métodos específicos para señales de audio.
    """

    def __init__(self, datos, frecuencia_muestreo: int):
        """
        Inicializa la señal de audio.

        Args:
            datos: Los datos que representan la señal de audio.
            frecuencia_muestreo: La frecuencia de muestreo de la señal en Hz.
        """
        super().__init__(datos)
        self.frecuencia_muestreo = frecuencia_muestreo

    def obtener_duracion(self) -> int:
        """
        Calcula la duración de la señal de audio en segundos.

        Returns:
            float: Duración de la señal en segundos.
        """
        return len(self.datos) / self.frecuencia_muestreo

class SenialAudioWAV(SenialAudio):
    """
    Clase que representa una señal de audio en formato WAV.

    Esta clase hereda de SenialAudio y puede agregar métodos específicos para
    manipular archivos WAV, como cargar desde un archivo o guardar en un archivo.
    """

    def __init__(self, ruta_archivo):
        """
        Inicializa la señal de audio WAV a partir de un archivo.

        Args:
            ruta_archivo: Ruta al archivo WAV.
        """
        
        frecuencia_muestreo, audio_data = wavfile.read(ruta_archivo)
        super().__init__(audio_data, frecuencia_muestreo)

    def guardar(self, ruta_archivo) -> None:
        """
        Guarda la señal de audio WAV en un archivo.

        Args:
            ruta_archivo: Ruta donde se guardará el archivo WAV.
        """
        wavfile.write(ruta_archivo, self.frecuencia_muestreo, self.datos)