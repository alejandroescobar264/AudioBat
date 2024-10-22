import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
from pathlib import Path

# Filtro pasa altos
def highpass_filter(data, rate, cutoff=15000, order=5):
    nyquist = 0.5 * rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
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

# Función para graficar la señal de audio completa
def plot_full_audio(audio_data, sample_rate):
    # Eliminar componente de continua restando la media
    audio_data_dc_remove = remove_dc_component(audio_data)
    audio_times = np.arange(len(audio_data)) / sample_rate
    
    plt.figure(figsize=(12, 8))

    # Subplot para la señal original
    plt.subplot(2, 1, 1)
    plt.plot(audio_times, audio_data, color='b', alpha=0.6)
    plt.title('Audio Signal (Complete)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.grid()

    # Subplot para la señal con DC eliminado
    plt.subplot(2, 1, 2)
    plt.plot(audio_times, audio_data_dc_remove, color='r', alpha=0.6)
    plt.title('Audio Signal (Complete, DC Removed)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.grid()

    plt.tight_layout()
    plt.show()

# Función para graficar la región recortada y la señal filtrada
def plot_segment_and_filtered(audio_segment, filtered_segment, sample_rate, start_time, duration):
    # Eliminar componente de continua restando la media
    audio_segment = remove_dc_component(audio_segment)
    filtered_segment = remove_dc_component(filtered_segment)

    audio_times = np.arange(len(audio_segment)) / sample_rate + start_time

    plt.figure(figsize=(12, 8))

    # Subplot para la señal recortada
    plt.subplot(2, 1, 1)
    plt.plot(audio_times, audio_segment, color='b', alpha=0.6)
    plt.title('Audio Signal (Segment, DC Removed)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.grid()

    # Subplot para la señal filtrada
    plt.subplot(2, 1, 2)
    plt.plot(audio_times, filtered_segment, color='g', alpha=0.6)
    plt.title('Filtered Audio Signal (DC Removed)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.grid()

    plt.tight_layout()
    plt.show()

# Procesar un archivo de audio
def process_audio(file_path, start_time, duration, cutoff):
    # Cargar el archivo de audio
    fs, audio_data = wavfile.read(file_path)

    # Asegurarse de que el audio sea mono
    if audio_data.ndim > 1:
        audio_data = audio_data[:, 0]  # Tomar solo el primer canal si es estéreo

    # Calcular métricas del archivo de audio
    calculate_audio_metrics(audio_data, fs)

    # Graficar la señal de audio completa
    plot_full_audio(audio_data, fs)

    # Recortar la sección deseada
    start_sample = int(fs * start_time)
    end_sample = start_sample + int(fs * duration)
    audio_segment = audio_data[start_sample:end_sample]

    # Aplicar filtro pasa altos
    filtered_audio_segment = highpass_filter(audio_segment, fs, cutoff=cutoff)

    # Graficar la región recortada y la señal filtrada
    plot_segment_and_filtered(audio_segment, filtered_audio_segment, fs, start_time, duration)

# Configuración inicial
input_file = Path("Audio/Grabaciones/AR3/M_molossus.wav")
start = 0  # Segundos en los que empieza la sección
duration = 10  # Duración en segundos de la sección a analizar
cutoff = 15000  # Frecuencia de corte para el filtro pasa altos

# Procesar la sección del archivo de audio
process_audio(input_file, start, duration, cutoff)
