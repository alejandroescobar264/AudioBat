from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from modelo.senial import SenialAudio

class AudioProcessor(ABC):
    """
    Clase Base Abstracta para procesadores de señal de audio.

    Esta clase define una interfaz común para todos los procesadores de señal de audio.
    Las subclases deben heredar de esta clase e implementar los métodos abstractos
    `process` y `get_processed_data` para realizar el procesamiento específico y
    devolver la señal procesada.
    """

    def __init__(self, senial_audio: SenialAudio):
        """
        Inicializa el procesador con la frecuencia de muestreo (fs) y los datos de audio.

        Args:
            fs (float): Frecuencia de muestreo del audio.
            audio_data (np.ndarray): Arreglo de NumPy con los datos del audio.
        """
        self.fs = senial_audio.frecuencia_muestreo
        self.audio_data = senial_audio.datos
        self._processed_data = None

    @abstractmethod
    def process(self) -> None:
        """
        Método abstracto que define el procesamiento de la señal de audio.

        Este método debe implementarse en las subclases para realizar el procesamiento
        específico de cada tipo de procesador.
        """
        # Asegurarse de que el audio sea mono
        if self.audio_data.ndim > 1:
            self.audio_data = self.audio_data[:, 0]  # Tomar solo el primer canal si es estéreo
            

    def get_processed_data(self) -> np.ndarray:
        """
        Devuelve la señal de audio procesada.

        Returns:
            np.ndarray: Arreglo de NumPy con los datos del audio procesado.
        """
        if self._processed_data is None:
            raise Exception("La señal aún no ha sido procesada. Llame al método `process` primero.")
        return self._processed_data


class Segmenter(AudioProcessor):
    """
    Clase Segmenter para extraer un segmento específico de la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, start_time: int, duration: int):
        """
        Inicializa el procesador Segmentador.

        Args:
            fs (float): Frecuencia de muestreo del audio.
            audio_data (np.ndarray): Arreglo de NumPy con los datos del audio.
            start_time (float): Tiempo de inicio del segmento en segundos.
            duration (float): Duración del segmento en segundos.
        """
        super().__init__(senial_audio)
        self.start_time = start_time
        self.duration = duration

    def process(self) -> None:
        """
        Extrae el segmento de audio especificado.
        """
        start_sample = int(self.start_time * self.fs)
        end_sample = start_sample + int(self.duration * self.fs)
        self._processed_data = self.audio_data[start_sample:end_sample]
        
        # Crear un nuevo objeto SenialAudio con los datos procesados
        processed_signal = SenialAudio(self._processed_data, self.fs)
        self._processed_data = processed_signal

class HighPassFilter(AudioProcessor):
    """
    Clase HighPassFilter para aplicar un filtro pasa altos a la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, cutoff_freq, order=5):
        """
        Inicializa el procesador HighPassFilter.

        Args:
            fs (float): Frecuencia de muestreo del audio.
            audio_data (np.ndarray): Arreglo de NumPy con los datos del audio.
            cutoff (float): Frecuencia de corte del filtro en Hz.
            order (int, optional): Orden del filtro. Defaults to 5.
        """
        super().__init__(senial_audio)
        self.cutoff_freq = cutoff_freq
        self.order = order

    def process(self) -> None:
        """
        Aplica el filtro pasa altos a la señal de audio.
        """
        nyquist = 0.5 * self.fs
        normal_cutoff = self.cutoff_freq / nyquist
        b, a = butter(self.order, normal_cutoff, btype='high', analog=False)
        self._processed_data = filtfilt(b, a, self.audio_data)
        
        # Crear un nuevo objeto SenialAudio con los datos procesados
        processed_signal = SenialAudio(self._processed_data, self.fs)
        self._processed_data = processed_signal

class LowPassFilter(AudioProcessor):
    """
    Clase LowPassFilter para aplicar un filtro pasa bajos a la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, cutoff_freq, order=5):
        """
        Inicializa el procesador LowPassFilter.

        Args:
            fs (float): Frecuencia de muestreo del audio.
            audio_data (np.ndarray): Arreglo de NumPy con los datos del audio.
            cutoff (float): Frecuencia de corte del filtro en Hz.
            order (int, optional): Orden del filtro. Defaults to 5.
        """
        super().__init__(senial_audio)
        self.cutoff_freq = cutoff_freq
        self.order = order

    def process(self) -> None:
        """
        Aplica el filtro pasa bajos a la señal de audio.
        """
        nyquist = 0.5 * self.fs
        normal_cutoff = self.cutoff_freq / nyquist
        b, a = butter(self.order, normal_cutoff, btype='low', analog=False)
        self._processed_data = filtfilt(b, a, self.audio_data)
        
        # Crear un nuevo objeto SenialAudio con los datos procesados
        processed_signal = SenialAudio(self._processed_data, self.fs)
        self._processed_data = processed_signal


class DCRemover(AudioProcessor):
    """
    Clase DCRemover para eliminar la componente de continua de una señal de audio.
    """

    def process(self) -> None:
        """
        Elimina la componente de continua de la señal.
        """
        self._processed_data = (self.audio_data - np.mean(self.audio_data) )
        
        # Crear un nuevo objeto SenialAudio con los datos procesados
        processed_signal = SenialAudio(self._processed_data, self.fs)
        self._processed_data = processed_signal


class FFTProcessor(AudioProcessor):
    """
    Clase para aplicar la Transformada Rápida de Fourier (FFT) a una señal de audio.
    """
    def __init__(self, senial_audio: SenialAudio):
        """
        Inicializa el procesador FFTProcessor.
        
        """
        super().__init__(senial_audio)
        self.freqs = None
        
    def process(self) -> None:
        """
        Aplica la FFT a la señal de audio y calcula el espectro de frecuencias.
        """
        # Aplicar la FFT
        n = len(self.audio_data)
        fft_values = np.fft.fft(self.audio_data)
        fft_freqs = np.fft.fftfreq(n, d=1/self.fs)

        # Obtener magnitudes y limitar a frecuencias positivas
        self._processed_data = np.abs(fft_values[:n//2])
        self.freqs = fft_freqs[:n//2]
        
        return self._processed_data, self.freqs, self.fs

class EventProcessor(AudioProcessor):
    """
    Clase para detectar eventos dentro de la señal de audio.
    """
    def __init__(self, senial_audio: SenialAudio, energy_threshold, min_duration, focus_freq, output_dir, filename):
        """
        Inicializa el procesador EventProcessor.

        Args:
            senial_audio: La señal de audio a procesar.
            energy_threshold: Umbral de energía para la detección de eventos.
            min_duration: Duración mínima (en segundos) para considerar un evento.
        """
        super().__init__(senial_audio)
        self.events = None
        self.energy_threshold = energy_threshold
        self.segment_duration_ms = 6
        self.segment_duration = self.segment_duration_ms / 1000  # Convertir a segundos
        self.min_duration = min_duration
        self.focus_freq = focus_freq
        self._filename = output_dir / f"{filename}_events.csv"

    def process(self) -> None:
        """
        Procesa la señal de audio para detectar eventos.

        1. Segmenta la señal en trozos de 6 ms.
        2. Calcula la energía de cada segmento.
        3. Detecta eventos basados en la energía y duración.
        4. Guarda los eventos detectados en un archivo CSV.
        5. Genera un espectrograma con los eventos marcados
        """
        segments = self._segmentar_audio()
        self._detectar_eventos(segments)
        self._guardar_csv()
        self._visualizar_eventos()
            

    def _segmentar_audio(self):
        """Divide la señal de audio en segmentos de duración fija."""
        segment_samples = int(self.segment_duration * self.fs)
        segments = [self.audio_data[i:i+segment_samples] for i in range(0, len(self.audio_data), segment_samples)]
        return segments

    def _calcular_energia(self, segment):
        """Calcula la energía de un segmento de audio."""
        return np.sum(segment**2)

    def _detectar_eventos(self, segments):
        """Detecta eventos basados en la energía y duración."""
        self.events = []
        current_event = None
        for i, segment in enumerate(segments):
            energy = self._calcular_energia(segment)  # Use only the segment argument
            if energy > self.energy_threshold:
                if current_event is None:
                    current_event = [i]
            else:
                if current_event and i - current_event[0] >= self.min_duration:
                    start_time = current_event[0] * self.segment_duration
                    end_time = i * self.segment_duration
                    self.events.append((start_time, end_time))
                current_event = None

    def _guardar_csv(self):
        """Guarda los eventos en un archivo CSV."""
        if self.events is None:
            print("No se detectaron eventos.")
            return  # Early exit if no events were found

        data = []
        for start, end in self.events:
            duration_ms = (end - start) / self.fs * 1000  # Convertir a milisegundos
            data.append([start, end, duration_ms])
        df = pd.DataFrame(data, columns=['Inicio', 'Fin', 'Duración (ms)'])
        df.to_csv(self._filename, index=False)
    
    
    def _visualizar_eventos(self):
        """
        Visualiza el espectrograma del segmento y marca los eventos.
        Recorta los eventos y los guarda como archivos de audio.
        """
        # Calcular el espectrograma
        Sxx, freqs, times, im = plt.specgram(self.audio_data, Fs=self.fs, NFFT=1024, noverlap=512, cmap='binary')

        
        # Crear figura y ejes
        fig, ax = plt.subplots(figsize=(10, 4))
        
        if self.focus_freq is not None:
            freq_mask = np.logical_and(freqs >= self.focus_freq[0], freqs <= self.focus_freq[1])
            plt.pcolormesh(times, freqs[freq_mask], 10 * np.log10(Sxx[freq_mask, :]), shading='gouraud', cmap='binary')
            plt.ylim(self.focus_freq)  # Limitar las frecuencias visibles al rango de enfoque
        else:
            plt.pcolormesh(times, freqs, 10 * np.log10(Sxx), shading='gouraud', cmap='binary')
        
        
        plt.title(f'Spectrogram of Filtered Audio Segment')
        plt.ylabel('Frecuencia (Hz)')
        plt.xlabel('Tiempo (s)')
        plt.colorbar(label='Intensidad (dB)', location='bottom')

        plt.tight_layout()

        # Agregar marcas para los eventos
        for start_time, end_time in self.events:
            ax.axvline(x=start_time, color='red', linestyle='--')
            ax.axvline(x=end_time, color='red', linestyle='--')
        

        # Guardar la figura
        plt.savefig("espectograma_con_eventos.png")
        plt.close()