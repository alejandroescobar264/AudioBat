from abc import ABC, abstractmethod
from scipy.io import wavfile  # Importar la librería soundfile para leer archivos WAV
from typing import Any
import numpy as np
import matplotlib.pyplot as plt

class SenialBase(ABC):
    """
    Clase abstracta que representa una señal.

    Esta clase define una interfaz común para todas las señales,
    especificando los métodos que deben implementarse en las subclases.
    """

    def __init__(self, datos: Any):
        """
        Inicializa la señal con los datos.

        Args:
            datos: Los datos que representan la señal (puede ser una lista, un array de NumPy, etc.).
        """
        self.datos = datos

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
    
    def __len__(self):
        return len(self.datos)

    
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
    
    def __len__(self):
        return len(self.datos)

    
    def guardar(self, ruta_archivo) -> None:
        """
        Guarda la señal de audio WAV en un archivo.

        Args:
            ruta_archivo: Ruta donde se guardará el archivo WAV.
        """
        wavfile.write(ruta_archivo, self.frecuencia_muestreo, self.datos)
    
    # Función para calcular métricas del archivo de audio
    def metricas(self):
        duracion = self.obtener_duracion()
        energy = np.sum(self.datos**2)  # Energía total de la señal
        max_amplitude = np.max(np.abs(self.datos))  # Amplitud máxima
        dynamic_range = 20 * np.log10(max_amplitude / np.mean(np.abs(self.datos)))  # Rango dinámico en dB
        rms = np.sqrt(np.mean(self.datos**2))  # Valor RMS de la señal

        #print(f"        Duración: {duracion:.2f} segundos")
        #print(f"        Energía total: {energy:.2e}")
        #print(f"        Amplitud máxima: {max_amplitude}")
        #print(f"        Rango dinámico: {dynamic_range:.2f} dB")
        #print(f"        Valor RMS: {rms:.4f}")
        
        # Crear el diccionario con las métricas
        metricas_dict = {
            "duracion": round(duracion, 2),
            "energia_total": float(energy),
            "amplitud_maxima": float(max_amplitude),
            "rango_dinamico_db": round(dynamic_range, 4),
            "valor_rms": round(rms, 4)
        }
        
        return metricas_dict