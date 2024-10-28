"""
Clase para generar la salida y visualización del contenido de la señal.
"""

from modelo.senial import SenialAudio
from procesador.procesador import EventProcessor
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

class Visualizador:
    """
    Clase que proporciona métodos para visualizar y guardar gráficos de la señal de audio
    y sus espectros asociados.
    """

    def __init__(self, output_dir: Path, filename: str) -> None:
        """
        Inicializa el visualizador.

        Args:
            output_dir (Path): Directorio donde se guardarán las visualizaciones.
            filename (str): Nombre base del archivo para las visualizaciones.
        """
        self.output_dir: Path = output_dir
        self.filename: str = filename

    def plot_spectrum(self, magnitudes: np.ndarray, freqs: np.ndarray, fs: float) -> None:
        """
        Grafica el espectro de frecuencias de la señal.

        Args:
            magnitudes (np.ndarray): Array con las magnitudes del espectro de frecuencias.
            freqs (np.ndarray): Array con las frecuencias correspondientes.
            fs (float): Frecuencia de muestreo de la señal.
        """
        plt.figure(figsize=(12, 6))
        plt.plot(freqs, magnitudes, color='purple', alpha=0.7)
        plt.title(f'Frequency Spectrum $\\bf{{{self.filename}}}$')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.xlim(0, fs / 2)
        plt.grid()
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{self.filename}_frequency_spectrum.png", dpi=300)
        plt.close()

    def plot_audio(self, senial_audio: SenialAudio) -> None:
        """
        Grafica la señal de audio completa.

        Args:
            senial_audio (SenialAudio): Objeto con la señal de audio a graficar.
        """
        audio_times = np.arange(len(senial_audio.datos)) / senial_audio.frecuencia_muestreo

        plt.figure(figsize=(12, 8))
        plt.plot(audio_times, senial_audio.datos, color='b', alpha=0.6)
        plt.title(f'Audio Signal $\\bf{{{self.filename}}}$ (Complete)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        plt.xlim([audio_times[0], audio_times[-1]])
        plt.savefig(self.output_dir / f"{self.filename}_complete_signal.png", dpi=300)
        plt.close()

    def plot_audio_segment_filtrado(self, audio_segment: SenialAudio, filtered_segment: SenialAudio, start_time: float) -> None:
        """
        Grafica un segmento de audio y su versión filtrada.

        Args:
            audio_segment (SenialAudio): Segmento de audio original.
            filtered_segment (SenialAudio): Segmento de audio después de la filtración.
            start_time (float): Tiempo de inicio del segmento en segundos.
        """
        audio_times = np.arange(len(audio_segment.datos)) / audio_segment.frecuencia_muestreo + start_time

        plt.figure(figsize=(12, 8))

        # Señal recortada
        plt.subplot(2, 1, 1)
        plt.plot(audio_times, audio_segment.datos, color='b', alpha=0.6)
        plt.title(f'Audio Signal $\\bf{{{self.filename}}}$ (Segment, DC Removed)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        plt.xlim([audio_times[0], audio_times[-1]])

        # Señal filtrada
        plt.subplot(2, 1, 2)
        plt.plot(audio_times, filtered_segment.datos, color='g', alpha=0.6)
        plt.title(f'Filtered Audio Signal $\\bf{{{self.filename}}}$ (HighPass + LowPass)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        plt.xlim([audio_times[0], audio_times[-1]])

        plt.tight_layout()
        plt.savefig(self.output_dir / f"{self.filename}_segment_filtered.png", dpi=300)
        plt.close()

    def plot_audio_segment_and_spectrogram(self, audio_segment: SenialAudio, start_time: float, focus_freq: tuple[int, int] = None) -> None:
        """
        Grafica un segmento de audio y su espectrograma.

        Args:
            audio_segment (SenialAudio): Segmento de audio.
            start_time (float): Tiempo de inicio del segmento en segundos.
            focus_freq (tuple, optional): Rango de frecuencias a mostrar en el espectrograma.
        """
        fs = audio_segment.frecuencia_muestreo
        audio_times = np.arange(len(audio_segment.datos)) / fs + start_time

        plt.figure(figsize=(12, 8))

        # Señal filtrada
        plt.subplot(2, 1, 1)
        plt.plot(audio_times, audio_segment.datos, color='g', alpha=0.6)
        plt.title(f'Filtered Audio Signal $\\bf{{{self.filename}}}$ (HighPass + LowPass)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()

        plt.xlim([audio_times[0], audio_times[-1]])

        # Espectrograma
        plt.subplot(2, 1, 2)
        Sxx, freqs, times, _ = plt.specgram(audio_segment.datos, Fs=fs, NFFT=1024, noverlap=512, cmap='binary')
        
        if focus_freq:
            freq_mask = np.logical_and(freqs >= focus_freq[0], freqs <= focus_freq[1])
            plt.pcolormesh(times, freqs[freq_mask], 10 * np.log10(Sxx[freq_mask, :]), shading='gouraud', cmap='binary')
            plt.ylim(focus_freq)
        else:
            plt.pcolormesh(times, freqs, 10 * np.log10(Sxx), shading='gouraud', cmap='binary')

        plt.title(f'Spectrogram of Filtered Audio Segment $\\bf{{{self.filename}}}$')
        plt.ylabel('Frecuencia (Hz)')
        plt.xlabel('Tiempo (s)')
        plt.colorbar(label='Intensidad (dB)', location='bottom')

        plt.xlim([audio_times[0], audio_times[-1]])

        plt.tight_layout()
        plt.savefig(self.output_dir / f"{self.filename}_spectrogram_segment.png")
        plt.close()

    def plot_spectrogram_events_complete(self, event_processor: EventProcessor) -> None:
        """
        Grafica el espectrograma de la señal completa y marca los eventos detectados.

        Args:
            event_processor (EventProcessor): Procesador que contiene los eventos detectados.
        """
        fs = event_processor.fs
        Sxx, freqs, times, _ = plt.specgram(event_processor.audio_data, Fs=fs, NFFT=1024, noverlap=512, cmap='binary')

        plt.figure(figsize=(10, 4))

        if event_processor.focus_freq:
            freq_mask = np.logical_and(freqs >= event_processor.focus_freq[0], freqs <= event_processor.focus_freq[1])
            plt.pcolormesh(times, freqs[freq_mask], 10 * np.log10(Sxx[freq_mask, :]), shading='gouraud', cmap='binary')
            plt.ylim(event_processor.focus_freq)
        else:
            plt.pcolormesh(times, freqs, 10 * np.log10(Sxx), shading='gouraud', cmap='binary')

        plt.title(f'Spectrogram With Detected Events of $\\bf{{{self.filename}}}$')
        plt.ylabel('Frecuencia (Hz)')
        plt.xlabel('Tiempo (s)')
        plt.colorbar(label='Intensidad (dB)', location='bottom')

        # Marcar eventos
        for start_time, end_time in event_processor.events:
            plt.axvline(x=start_time, color='red', linestyle='--')
            plt.axvline(x=end_time, color='red', linestyle='--')

        os.makedirs(self.output_dir / "eventos", exist_ok=True)
        plt.savefig(self.output_dir / "eventos" / f"{self.filename}_spectrogram_events.png")
        plt.close()

    def plot_spectrogram_events_single(self, event_processor: EventProcessor) -> None:
        """
        Grafica y guarda el espectrograma de cada evento individual detectado.

        Args:
            event_processor (EventProcessor): Procesador que contiene los eventos detectados.
        """
        fs = event_processor.fs

        for i, (start_time, end_time) in enumerate(event_processor.events):
            buffer_ms = 100  # Margen adicional de 10 ms
            adjusted_start_time = max(0, start_time - buffer_ms / 1000)
            adjusted_end_time = min(len(event_processor.audio_data) / fs, end_time + buffer_ms / 1000)

            start_index = int(adjusted_start_time * fs)
            end_index = int(adjusted_end_time * fs)
            event_audio = event_processor.audio_data[start_index:end_index]

            Sxx_event, freqs_event, times_event, _ = plt.specgram(event_audio, Fs=fs, NFFT=1024, noverlap=512, cmap='binary')

            plt.figure()
            
            if event_processor.focus_freq:
                freq_mask = np.logical_and(freqs_event >= event_processor.focus_freq[0], freqs_event <= event_processor.focus_freq[1])
                plt.pcolormesh(times_event, freqs_event[freq_mask], 10 * np.log10(Sxx_event[freq_mask, :]), shading='gouraud', cmap='binary')
                plt.ylim(event_processor.focus_freq)
            else:
                plt.pcolormesh(times_event, freqs_event, 10 * np.log10(Sxx_event), shading='gouraud', cmap='binary')

            plt.title(f"Espectrograma del evento {i}")
            plt.ylabel('Frecuencia (Hz)')
            plt.xlabel('Tiempo (s)')
            plt.colorbar(label='Intensidad (dB)', location='bottom')
            plt.tight_layout()

            os.makedirs(self.output_dir / "eventos" / "individuales", exist_ok=True)
            plt.savefig(self.output_dir / "eventos" / "individuales" / f"espectograma_evento_{i}.png")
            plt.close()
