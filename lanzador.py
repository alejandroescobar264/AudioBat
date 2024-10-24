__author__ = 'Alejandro Escobar'
__version__ = '1.0.0'
__date__ = '2024/10/22'
__author_email__ = 'alejandroescobar264@gmail.com'

"""
Las responsabilidades se dividen entre diferentes clases separadas en diferentes módulos a implementar.
"""
import os
from pathlib import Path
import modelo.senial
import procesador
import procesador.procesador
import visualizador.visualizador
import reportador.reportador



class Lanzador:
    """
    Programa Lanzador
    """

    @staticmethod
    def tecla() -> None:
        """
        Función que solicita al usuario presionar cualquier tecla para continuar.

        Esta función espera cualquier entrada del usuario y luego limpia la pantalla.
        """
        input("Presione cualquier tecla para continuar...")
        os.system('clear')

    @staticmethod
    def informar_versiones() -> None:
        """
        Informa las versiones de los componentes
        """
        os.system("clear")
        print("Versiones de los componentes")
        print(f"modelo: {modelo.__version__}")
        print(f"visualizador: {visualizador.__version__}")
        print(f"procesador: {procesador.__version__}")
        print(f"reportador: {reportador.__version__}")

    @staticmethod
    def ejecutar() -> None:
        """
        Programa principal
        """
        # Se prepara el programa
        Lanzador.informar_versiones()
        Lanzador.tecla()


        os.system("clear")
        print("Inicio - Paso 1 - Carga de la señal")
        # Paso 1 - Se carga la senial
        # Cargar la señal de audio
        
        ruta_archivo = Path("Audio/Grabaciones/AR1/AR1ecAR1303712_20240918_012907.wav")
        senial_audio = modelo.senial.SenialAudioWAV(ruta_archivo)
        
                
        # Crear carpeta de salida basada en el nombre del archivo de audio
        ruta_salida = Path("Salidas") / ruta_archivo.stem
        os.makedirs(ruta_salida, exist_ok=True)
        
        # Se instancian las clases que participan del procesamiento
        mi_procesador = procesador.procesador
        mi_visualizador = visualizador.visualizador.Visualizador(ruta_salida, ruta_archivo.stem)
        mi_reportador = reportador.reportador
        
        # Mostrar métricas
        print("    |--> Métricas de la señal")
        print(senial_audio.metricas())

        # Paso 2 - Se procesa la senial adquirida
        print("Inicio - Paso 2 - Procesamiento")
        
        print("    |--> Se resta la continua")
        DCRemover = mi_procesador.DCRemover(senial_audio)
        DCRemover.process()
        senial_audio_dc_remove = DCRemover.get_processed_data()

        print("    |--> Se segmenta la señal")
        # Segmentar los primeros 10 segundos
        start_time = 0
        duration = 10
        segmentador = mi_procesador.Segmenter(senial_audio_dc_remove, start_time, duration)
        segmentador.process()
        segmento_senial = segmentador.get_processed_data()

        print("    |--> Se filtra la señal")
        # Aplicar filtros
        filtro_pasa_altos = mi_procesador.HighPassFilter(segmento_senial, cutoff_freq=2500)
        filtro_pasa_altos.process()
        segmento_senial_filtrada_altos = filtro_pasa_altos.get_processed_data()

        filtro_pasa_bajos = mi_procesador.LowPassFilter(segmento_senial_filtrada_altos, cutoff_freq=5000)
        filtro_pasa_bajos.process()
        segmento_senial_filtrada = filtro_pasa_bajos.get_processed_data()
        
        print("    |--> Se calcula la FFT de la señal")
        fft_processor = mi_procesador.FFTProcessor(segmento_senial_filtrada)
        magitudes, frecuencia, frecuencia_muestreo = fft_processor.process()
        
        print("    |--> Se expande temporalmente")
        time_expansion_factor = 10
        time_expansor = mi_procesador.TimeExpander(segmento_senial_filtrada, time_expansion_factor)
        time_expansor.process()
        segmento_senial_expandida = time_expansor.get_processed_data()
        
        # Paso 3 - Se detectan eventos
        print("Inicio - Paso 3 - Detectar Eventos")
        energy_threshold = 1e+6  # Umbral de energía
        min_duration_ms = 20  # Duración mínima de una vocalización en ms
        focus_freq = (1500,5000)  # Rango de frecuencia para el espectrograma (opcional)
        event_processor = mi_procesador.EventProcessor(segmento_senial_filtrada, energy_threshold, min_duration_ms, focus_freq, ruta_salida, ruta_archivo.stem)
        event_processor.process()

        # Paso 4 - Se muestran las seniales
        print("Inicio - Paso 4 - Mostrar Señales")
        
        # Visualizar los resultados
        print("    |--> Guardar señal audio completa")
        mi_visualizador.plot_audio(senial_audio)
        print("    |--> Guardar segmento filtrado")
        mi_visualizador.plot_audio_segment_filtrado(segmento_senial, segmento_senial_filtrada, start_time)
        print("    |--> Guardar espectrograma del segmento")
        mi_visualizador.plot_audio_segment_and_spectrogram(segmento_senial, start_time, focus_freq)
        print("    |--> Guardar espectrograma con eventos")
        mi_visualizador.plot_spectrogram_events_complete(event_processor)
        print("    |--> Guardar espectrograma de cada evento")
        mi_visualizador.plot_spectrogram_events_single(event_processor)
        print("    |--> Guardar espectro frecuencias")
        mi_visualizador.plot_spectrum(magitudes, frecuencia, frecuencia_muestreo)
        
        # Paso 5 - Generar Reportes
        print("Inicio - Paso 5 - Generar Reportes")
        
        # Crear un objeto de reporte
        mi_reportador_json = mi_reportador.JSONReportGenerator(ruta_salida)

        # Generar el reporte
        mi_reportador_json.generate_report(senial_audio, segmentador, filtro_pasa_altos, filtro_pasa_bajos, event_processor)
        
        
if __name__ == "__main__":
    Lanzador().ejecutar()