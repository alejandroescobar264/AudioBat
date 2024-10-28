import json
import os
from modelo.senial import SenialAudio
from procesador.procesador import Segmenter, HighPassFilter, LowPassFilter, EventProcessor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from abc import ABC, abstractmethod
from typing import Union, Dict, Any, List


class ReportGenerator(ABC):
    """
    Clase base abstracta para generar reportes.
    Define la interfaz para las clases de generación de reportes.
    """

    def __init__(self, output_dir: Union[str, os.PathLike]):
        """
        Inicializa el generador de reportes.

        Args:
            output_dir (Union[str, os.PathLike]): Directorio donde se guardará el reporte.
        """
        self.output_dir: Union[str, os.PathLike] = output_dir

    @abstractmethod
    def generate_report(self, *args, **kwargs) -> None:
        """
        Método abstracto para generar el reporte.
        Debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclases deben implementar este método")


class JSONReportGenerator(ReportGenerator):
    """
    Clase para generar un reporte en formato JSON con los resultados del análisis de señal de audio.
    """

    def __init__(self, output_dir: Union[str, os.PathLike]):
        """
        Inicializa el generador de reportes JSON.

        Args:
            output_dir (Union[str, os.PathLike]): Directorio donde se guardará el reporte JSON.
        """
        super().__init__(output_dir)

    def generate_report(self, senial_audio: SenialAudio, segmenter: Segmenter, 
                        filtro_hp: HighPassFilter, filtro_lp: LowPassFilter, 
                        event_processor: EventProcessor) -> None:
        """
        Genera un reporte en formato JSON con métricas y parámetros de análisis.

        Args:
            senial_audio (SenialAudio): Señal de audio procesada.
            segmenter (Segmenter): Segmentador de la señal.
            filtro_hp (HighPassFilter): Filtro pasa-altos.
            filtro_lp (LowPassFilter): Filtro pasa-bajos.
            event_processor (EventProcessor): Procesador de eventos.
        """
        # Obtener datos relevantes
        file_path = str(self.output_dir)
        metrics = senial_audio.metricas()
        segment_start = segmenter.start_time
        segment_end = segment_start + segmenter.duration
        parameters = {
            'high_pass_cutoff': filtro_hp.cutoff_freq,
            'low_pass_cutoff': filtro_lp.cutoff_freq,
            'energy_threshold': event_processor.energy_threshold,
            'min_duration': event_processor.min_duration,
            'focus_freq': event_processor.focus_freq
        }
        events = event_processor.events

        # Crear el diccionario del reporte
        report = {
            "file_path": file_path,
            "metrics": metrics,
            "segment": {
                "start": segment_start,
                "end": segment_end
            },
            "parameters": parameters,
            "events": events
        }

        # Guardar el reporte en un archivo JSON
        with open(f"{self.output_dir}/{self.output_dir.stem}_report.json", "w") as f:
            json.dump(report, f, indent=4)


class PDFReportGenerator(ReportGenerator):
    """
    Clase para generar un reporte en formato PDF con los resultados del análisis de señal de audio.
    """

    def __init__(self, output_dir: Union[str, os.PathLike]):
        """
        Inicializa el generador de reportes PDF.

        Args:
            output_dir (Union[str, os.PathLike]): Directorio donde se guardará el reporte PDF.
        """
        super().__init__(output_dir)

    def generate_report(self, senial_audio: SenialAudio, segmenter: Segmenter, 
                        filtro_hp: HighPassFilter, filtro_lp: LowPassFilter, 
                        event_processor: EventProcessor) -> None:
        """
        Genera un reporte en formato PDF con métricas y parámetros de análisis.

        Args:
            senial_audio (SenialAudio): Señal de audio procesada.
            segmenter (Segmenter): Segmentador de la señal.
            filtro_hp (HighPassFilter): Filtro pasa-altos.
            filtro_lp (LowPassFilter): Filtro pasa-bajos.
            event_processor (EventProcessor): Procesador de eventos.
        """
        # Obtener datos relevantes
        file_path = str(self.output_dir)
        metrics = senial_audio.metricas()
        segment_start = segmenter.start_time
        segment_end = segment_start + segmenter.duration
        parameters = {
            'high_pass_cutoff': filtro_hp.cutoff_freq,
            'low_pass_cutoff': filtro_lp.cutoff_freq,
            'energy_threshold': event_processor.energy_threshold,
            'min_duration': event_processor.min_duration,
            'focus_freq': event_processor.focus_freq
        }
        events = event_processor.events

        # Formatear los eventos como una lista de diccionarios
        if events and isinstance(events[0], tuple):
            events = [{'inicio': e[0], 'fin': e[1]} for e in events]

        # Crear el reporte PDF
        report = canvas.Canvas(f"{self.output_dir}/{self.output_dir.stem}_report.pdf", pagesize=A4)

        # Configuración inicial del PDF
        report.setFont("Helvetica", 12)
        y_pos = 750  # Posición vertical inicial
        
        report.drawString(50, y_pos, f"Archivo analizado: {file_path}")
        y_pos -= 20

        # Escribir información de métricas
        for key, value in metrics.items():
            report.drawString(50, y_pos, f"{key}: {value}")
            y_pos -= 20

        # Segmento analizado
        report.drawString(50, y_pos, f"Segmento analizado: {segment_start} - {segment_end}")
        y_pos -= 20

        # Parámetros del análisis
        report.drawString(50, y_pos, "Parámetros del análisis:")
        y_pos -= 15
        for key, value in parameters.items():
            report.drawString(70, y_pos, f"{key}: {value}")
            y_pos -= 15

        # Títulos de la tabla de eventos
        report.drawString(50, y_pos, "Eventos:")
        y_pos -= 20
        report.drawString(70, y_pos, "Inicio")
        report.drawString(150, y_pos, "Fin")
        y_pos -= 15

        # Agregar eventos detectados al PDF
        for event in events:
            report.drawString(70, y_pos, str(event.get('inicio', 'N/A')))
            report.drawString(150, y_pos, str(event.get('fin', 'N/A')))
            y_pos -= 15

        report.showPage()  # Termina la página de contenido principal

        # Agregar imágenes al PDF desde un directorio
        def agregar_imagenes_desde_directorio(directorio: str) -> None:
            """
            Agrega todas las imágenes PNG de un directorio al PDF, cada imagen en una página nueva.

            Args:
                directorio (str): Ruta del directorio con las imágenes.
            """
            for filename in os.listdir(directorio):
                if filename.endswith(".png"):
                    img_path = os.path.join(directorio, filename)
                    report.drawImage(img_path, 50, 150, width=500, height=400)
                    report.showPage()

        # Agregar imágenes de salida y eventos
        agregar_imagenes_desde_directorio(self.output_dir)

        eventos_dir = os.path.join(self.output_dir, "eventos")
        if os.path.exists(eventos_dir):
            agregar_imagenes_desde_directorio(eventos_dir)

            # Agregar imágenes de eventos individuales
            individuales_dir = os.path.join(eventos_dir, "individuales")
            if os.path.exists(individuales_dir):
                agregar_imagenes_desde_directorio(individuales_dir)

        report.save()  # Guardar el archivo PDF
