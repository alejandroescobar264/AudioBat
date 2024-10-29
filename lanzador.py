__author__ = 'Alejandro Escobar'
__version__ = '1.0.0'
__date__ = '2024/10/22'
__author_email__ = 'alejandroescobar264@gmail.com'

"""
Este módulo implementa el programa principal de la aplicación.
Su responsabilidad es gestionar las operaciones de carga de señal, procesamiento, visualización y generación de reportes.
Las funcionalidades están divididas en diferentes módulos, cada uno con una responsabilidad específica.
"""

import os
from pathlib import Path
import modelo.senial  # Importa las clases para manejo de señales
import procesador  # Importa el módulo para procesar las señales
import procesador.procesador  # Importa los procesadores específicos
import visualizador.visualizador  # Importa el visualizador de datos
import reportador.reportador  # Importa el generador de reportes


class Lanzador:
    """
    Clase principal del programa, gestiona la ejecución del flujo de análisis.
    """

    @staticmethod
    def tecla() -> None:
        """
        Solicita al usuario presionar cualquier tecla para continuar y limpia la pantalla.
        """
        input("Presione cualquier tecla para continuar...")
        os.system('clear')

    @staticmethod
    def informar_versiones() -> None:
        """
        Informa las versiones de los componentes utilizados en el proyecto.
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
        Ejecuta el flujo principal de procesamiento de la señal de audio.
        """
        # Mostrar versiones y esperar entrada del usuario
        Lanzador.informar_versiones()
        Lanzador.tecla()

        os.system("clear")
        print("Inicio - Paso 1 - Carga de la señal")
        
        # Carga la señal de audio desde un archivo especificado
        ruta_archivo = Path("Audio/Grabaciones/AR1/AR1ecAR1303712_20240918_012907.wav")
        senial_audio = modelo.senial.SenialAudioWAV(ruta_archivo)
        
        # Configura las rutas de salida
        ruta_salida = Path("Salidas") / ruta_archivo.stem
        os.makedirs(ruta_salida, exist_ok=True)
        
        ruta_eventos = Path("Salidas") / ruta_archivo.stem / Path("eventos")
        os.makedirs(ruta_eventos, exist_ok=True)
        
        # Instancia los componentes de procesamiento y visualización
        mi_procesador = procesador.procesador
        mi_visualizador = visualizador.visualizador.Visualizador(ruta_salida, ruta_archivo.stem)
        mi_reportador = reportador.reportador
        
        # Muestra las métricas de la señal cargada
        print("    |--> Métricas de la señal")
        print(senial_audio.metricas())

        print("Inicio - Paso 2 - Procesamiento")
        
        # Elimina la componente de continua de la señal de audio
        print("    |--> Se resta la continua")
        DCRemover = mi_procesador.DCRemover(senial_audio)
        DCRemover.process()
        senial_audio_dc_remove = DCRemover.get_processed_data()

        # Segmenta la señal para obtener los primeros 10 segundos
        print("    |--> Se segmenta la señal")
        start_time = 0
        duration = 10
        segmentador = mi_procesador.Segmenter(senial_audio_dc_remove, start_time, duration)
        segmentador.process()
        segmento_senial = segmentador.get_processed_data()

        # Aplica filtros pasa-altos y pasa-bajos a la señal segmentada
        print("    |--> Se filtra la señal")
        filtro_pasa_altos = mi_procesador.HighPassFilter(segmento_senial, cutoff_freq=2500)
        filtro_pasa_altos.process()
        segmento_senial_filtrada_altos = filtro_pasa_altos.get_processed_data()

        filtro_pasa_bajos = mi_procesador.LowPassFilter(segmento_senial_filtrada_altos, cutoff_freq=5000)
        filtro_pasa_bajos.process()
        segmento_senial_filtrada = filtro_pasa_bajos.get_processed_data()
        
        # Calcula el espectro de frecuencias usando FFT
        print("    |--> Se calcula la FFT de la señal")
        fft_processor = mi_procesador.FFTProcessor(segmento_senial_filtrada)
        magitudes, frecuencia, frecuencia_muestreo = fft_processor.process()
        
        # Expande la señal en el tiempo para análisis detallado
        print("    |--> Se expande temporalmente")
        time_expansion_factor = 10
        time_expansor = mi_procesador.TimeExpander(segmento_senial_filtrada, time_expansion_factor)
        time_expansor.process()
        segmento_senial_expandida = time_expansor.get_processed_data()
        
        print("Inicio - Paso 3 - Detectar Eventos")
        # Detecta eventos en la señal de acuerdo a un umbral de energía y duración mínima
        energy_threshold = 1e+6
        min_duration_ms = 20
        focus_freq = (1500,5000)
        event_processor = mi_procesador.EventProcessor(segmento_senial_filtrada, energy_threshold, min_duration_ms, focus_freq, ruta_eventos, ruta_archivo.stem)
        event_processor.process()

        print("Inicio - Paso 4 - Mostrar Señales")
        
        # Visualiza y guarda gráficos de la señal y espectrogramas
        print("    |--> Guardar señal audio completa")
        mi_visualizador.plot_audio(senial_audio)
        print("    |--> Guardar segmento filtrado")
        mi_visualizador.plot_audio_segment_filtrado(segmento_senial, segmento_senial_filtrada, start_time)
        print("    |--> Guardar espectrograma del segmento")
        mi_visualizador.plot_audio_segment_and_spectrogram(segmento_senial_filtrada, start_time, focus_freq)
        print("    |--> Guardar espectrograma con eventos")
        mi_visualizador.plot_spectrogram_events_complete(event_processor)
        print("    |--> Guardar espectrograma de cada evento")
        mi_visualizador.plot_spectrogram_events_single(event_processor)
        print("    |--> Guardar espectro frecuencias")
        mi_visualizador.plot_spectrum(magitudes, frecuencia, frecuencia_muestreo)
        
        print("Inicio - Paso 5 - Generar Reportes")
        
        # Genera reportes en formato JSON y PDF
        print("    |--> Generar reportes JSON")
        mi_reportador_json = mi_reportador.JSONReportGenerator(ruta_salida)
        mi_reportador_json.generate_report(senial_audio, segmentador, filtro_pasa_altos, filtro_pasa_bajos, event_processor)
       
        print("    |--> Generar reportes PDF")
        mi_reportador_pdf = mi_reportador.PDFReportGenerator(ruta_salida)
        mi_reportador_pdf.generate_report(senial_audio, segmentador, filtro_pasa_altos, filtro_pasa_bajos, event_processor)
 

if __name__ == "__main__":
    Lanzador().ejecutar()
