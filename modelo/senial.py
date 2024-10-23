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
    
    def __len__(self):
        return len(self.datos)

    def graficar(self, output_dir, filename):
    
        audio_times = np.arange(len(self.datos)) / self.frecuencia_muestreo
        
        plt.figure(figsize=(12, 8))

        # Subplot para la señal original
        plt.plot(audio_times, self.datos, color='b', alpha=0.6)
        plt.title('Audio Signal (Complete)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        
        # Ajustar límites del eje x
        plt.xlim([audio_times[0], audio_times[-1]])
                            
        # Guardar la figura en formato PNG
        plt.savefig(output_dir / f"{filename}_complete_signal.png", dpi=300)
        plt.show()
        plt.close() 

    
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

    def graficar(self):
        pass  # Implementa la lógica de procesamiento si es necesario
    
    def graficar_segmento_filtrado(self, audio_segment, filtered_segment, start_time, output_dir, filename):
    
        audio_times = np.arange(len(audio_segment)) / self.frecuencia_muestreo + start_time

        plt.figure(figsize=(12, 8))

        # Subplot para la señal recortada
        plt.subplot(2, 1, 1)
        plt.plot(audio_times, audio_segment.datos, color='b', alpha=0.6)
        plt.title('Audio Signal (Segment, DC Removed)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        
        # Ajustar límites del eje x
        plt.xlim([audio_times[0], audio_times[-1]])

        # Subplot para la señal filtrada
        plt.subplot(2, 1, 2)
        plt.plot(audio_times, filtered_segment.datos, color='g', alpha=0.6)
        plt.title('Filtered Audio Signal (HighPass + LowPass)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        
        # Ajustar límites del eje x
        plt.xlim([audio_times[0], audio_times[-1]])

        plt.tight_layout()

        # Guardar la figura en formato PNG
        plt.savefig(output_dir / f"{filename}_segment_filtered.png", dpi=300)
        plt.close()

    
    def guardar(self, ruta_archivo) -> None:
        """
        Guarda la señal de audio WAV en un archivo.

        Args:
            ruta_archivo: Ruta donde se guardará el archivo WAV.
        """
        wavfile.write(ruta_archivo, self.frecuencia_muestreo, self.datos)