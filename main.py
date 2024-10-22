import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
from pathlib import Path
import os

# Filtro pasa altos
def highpass_filter(data, rate, cutoff=1500, order=5):
    nyquist = 0.5 * rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Filtro pasa bajos
def lowpass_filter(data, rate, cutoff=15000, order=5):
    nyquist = 0.5 * rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Función para restar la media y eliminar el componente de continua
def remove_dc_component(data):
    return data - np.mean(data)

# Función para calcular métricas del archivo de audio
def calculate_audio_metrics(audio_data, sample_rate):
    duration = len(audio_data) / sample_rate  # Duración en segundos
    energy = np.sum(audio_data**2)  # Energía total de la señal
    max_amplitude = np.max(np.abs(audio_data))  # Amplitud máxima
    dynamic_range = 20 * np.log10(max_amplitude / np.mean(np.abs(audio_data)))  # Rango dinámico en dB
    rms = np.sqrt(np.mean(audio_data**2))  # Valor RMS de la señal

    print("Métricas del archivo de audio:")
    print(f"Duración: {duration:.2f} segundos")
    print(f"Energía total: {energy:.2e}")
    print(f"Amplitud máxima: {max_amplitude}")
    print(f"Rango dinámico: {dynamic_range:.2f} dB")
    print(f"Valor RMS: {rms:.4f}")

# Función para graficar el espectro de frecuencias
def plot_frequency_spectrum(audio_segment, sample_rate, output_dir):
    # Aplicar la FFT
    n = len(audio_segment)
    fft_values = np.fft.fft(audio_segment)
    fft_freqs = np.fft.fftfreq(n, d=1/sample_rate)

    # Obtener magnitudes y limitar a frecuencias positivas
    magnitudes = np.abs(fft_values)
    positive_freqs = fft_freqs[:n // 2]
    positive_magnitudes = magnitudes[:n // 2]

    plt.figure(figsize=(12, 6))
    plt.plot(positive_freqs, positive_magnitudes, color='purple', alpha=0.7)
    plt.title('Frequency Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim(0, sample_rate / 2)  # Limitar a la mitad de la frecuencia de muestreo
    plt.grid()
    plt.tight_layout()
    plt.savefig(output_dir / f"{input_file.stem}_frequency_spectrum.png", dpi=300)
    plt.close()

# Función para graficar y guardar la señal de audio completa
def plot_full_audio(audio_data, sample_rate, output_dir, filename):
    
    audio_times = np.arange(len(audio_data)) / sample_rate
    
    plt.figure(figsize=(12, 8))

    # Subplot para la señal original
    plt.plot(audio_times, audio_data, color='b', alpha=0.6)
    plt.title('Audio Signal (Complete)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.grid()
    
    # Ajustar límites del eje x
    plt.xlim([audio_times[0], audio_times[-1]])
    
    # Guardar la figura en formato PNG
    plt.savefig(output_dir / f"{filename}_complete_signal.png", dpi=300)
    plt.close()

# Función para graficar y guardar la región recortada y la señal filtrada
def plot_segment_and_filtered(audio_segment, filtered_segment, sample_rate, start_time, duration, output_dir, filename):

    audio_times = np.arange(len(audio_segment)) / sample_rate + start_time

    plt.figure(figsize=(12, 8))

    # Subplot para la señal recortada
    plt.subplot(2, 1, 1)
    plt.plot(audio_times, audio_segment, color='b', alpha=0.6)
    plt.title('Audio Signal (Segment, DC Removed)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.grid()
    
    # Ajustar límites del eje x
    plt.xlim([audio_times[0], audio_times[-1]])

    # Subplot para la señal filtrada
    plt.subplot(2, 1, 2)
    plt.plot(audio_times, filtered_segment, color='g', alpha=0.6)
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

# Función para graficar la señal de audio filtrada y su espectrograma
def plot_segment_and_spectrogram(audio_segment, sample_rate, start_time, cutoff, focus_freq=None):

    # Graficar la señal filtrada
    audio_times = np.arange(len(audio_segment)) / sample_rate + start_time

    plt.figure(figsize=(12, 8))

    # Subplot para la señal filtrada
    plt.subplot(2, 1, 1)
    plt.plot(audio_times, audio_segment, color='g', alpha=0.6)
    plt.title('Filtered Audio Signal (HighPass + LowPass)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.grid()
    
    # Ajustar límites del eje x
    plt.xlim([audio_times[0], audio_times[-1]])

    # Subplot para el espectrograma
    plt.subplot(2, 1, 2)
    Sxx, freqs, times, im = plt.specgram(audio_segment, Fs=sample_rate, NFFT=1024, noverlap=512, cmap='inferno')
    
    if focus_freq is not None:
        freq_mask = np.logical_and(freqs >= focus_freq[0], freqs <= focus_freq[1])
        plt.pcolormesh(times, freqs[freq_mask], 10 * np.log10(Sxx[freq_mask, :]), shading='gouraud', cmap='inferno')
        plt.ylim(focus_freq)  # Limitar las frecuencias visibles al rango de enfoque
    else:
        plt.pcolormesh(times, freqs, 10 * np.log10(Sxx), shading='gouraud', cmap='inferno')

    plt.title('Spectrogram of Filtered Audio Segment')
    plt.ylabel('Frecuencia (Hz)')
    plt.xlabel('Tiempo (s)')
    plt.colorbar(label='Intensidad (dB)', location='bottom')

    # Ajustar límites del eje x
    plt.xlim([audio_times[0], audio_times[-1]])

    plt.tight_layout()
    
    # Crear carpeta de salida si no existe
    output_dir = Path("Salidas") / f"{input_file.stem}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar figura como PNG
    plt.savefig(output_dir / f"{input_file.stem}_spectrogram_segment.png")
    plt.close()

# Procesar un archivo de audio
def process_audio(file_path, start_time, duration, cutoff, focus_freq=None):
    # Cargar el archivo de audio
    fs, audio_data = wavfile.read(file_path)

    # Asegurarse de que el audio sea mono
    if audio_data.ndim > 1:
        audio_data = audio_data[:, 0]  # Tomar solo el primer canal si es estéreo
    
    # Crear carpeta de salida basada en el nombre del archivo de audio
    output_dir = Path("Salidas") / file_path.stem
    os.makedirs(output_dir, exist_ok=True)
    
    # Calcular métricas del archivo de audio
    calculate_audio_metrics(audio_data, fs)

    # Graficar y guardar la señal completa
    plot_full_audio(audio_data, fs, output_dir, file_path.stem)
    
    # Eliminar componente de continua restando la media
    audio_data_dc_remove = remove_dc_component(audio_data)

    # Definir el segmento de audio
    start_sample = int(start_time * fs)
    end_sample = start_sample + int(duration * fs)
    audio_segment = audio_data_dc_remove[start_sample:end_sample]
    
    # Filtrar el segmento
    filtered_segment_highass = highpass_filter(audio_segment, fs, cutoff)
    filtered_segment_lowpass = lowpass_filter(filtered_segment_highass, fs, cutoff)
    
    filtered_segment = filtered_segment_lowpass

    # Graficar el segmento y su señal filtrada
    plot_segment_and_filtered(audio_segment, filtered_segment, fs, start_time, duration, output_dir, file_path.stem)

    # Graficar el espectro de frecuencias del segmento
    plot_frequency_spectrum(filtered_segment, fs, output_dir)

    # Graficar el espectrograma del segmento
    plot_segment_and_spectrogram(filtered_segment, fs, start_time, cutoff, focus_freq)

# Parámetros de entrada
input_file = Path("Audio/Grabaciones/AR1/AR1ecAR1303712_20240918_012907.wav")  # Cambia esto por la ruta de tu archivo
start_time = 0  # Tiempo de inicio en segundos
duration = 10     # Duración del segmento en segundos
cutoff = 2500   # Frecuencia de corte para el filtro pasa altos
focus_freq = None  # Rango de frecuencia para el espectrograma (opcional)

# Procesar el archivo de audio
process_audio(input_file, start_time, duration, cutoff, focus_freq)
