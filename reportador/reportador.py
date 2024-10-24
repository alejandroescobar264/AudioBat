import json
import os
from modelo.senial import SenialAudio
from procesador.procesador import *
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    """Clase base para generar reportes"""

    def __init__(self, output_dir):
        self.output_dir = output_dir
        
    @abstractmethod
    def generate_report(self):
        raise NotImplementedError("Subclases deben implementar este método")

class JSONReportGenerator(ReportGenerator):
    
    def __init__(self, output_dir):
        """
        Inicializa el procesador FFTProcessor.
        
        """
        super().__init__(output_dir)
        
    
    def generate_report(self, senial_audio: SenialAudio, segmenter:Segmenter, filtro_hp:HighPassFilter, 
                        filtro_lp:LowPassFilter,  event_processor: EventProcessor):
        """Genera un reporte en formato JSON"""
        
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


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class PDFReportGenerator(ReportGenerator):

    def __init__(self, output_dir):
        super().__init__(output_dir)

    def generate_report(self, senial_audio: SenialAudio, segmenter: Segmenter, filtro_hp: HighPassFilter,
                        filtro_lp: LowPassFilter, event_processor: EventProcessor):
        """Genera un reporte en formato PDF"""

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

        # Manejo de eventos como tuplas
        if isinstance(events[0], tuple):  
            events = [{'inicio': e[0], 'fin': e[1]} for e in events]

        # Crear el reporte PDF
        report = canvas.Canvas(f"{self.output_dir}/{self.output_dir.stem}_report.pdf", pagesize=A4)

        # Establecer posición inicial para el contenido
        report.setFont("Helvetica", 12)
        y_pos = 750  # Iniciar en una posición más segura
        
        report.drawString(50, y_pos, f"Archivo analizado: {file_path}")
        y_pos -= 20

        # Escribir información general
        for key, value in metrics.items():
            report.drawString(50, y_pos, f"{key}: {value}")
            y_pos -= 20  # Reducir el espaciado de forma moderada

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

        # Agregar eventos
        for event in events:
            report.drawString(70, y_pos, str(event.get('inicio', 'N/A')))
            report.drawString(150, y_pos, str(event.get('fin', 'N/A')))
            y_pos -= 15

        # Finalizar la página de contenido principal
        report.showPage()

        # Función para agregar imágenes desde un directorio
        def agregar_imagenes_desde_directorio(directorio):
            for filename in os.listdir(directorio):
                if filename.endswith(".png"):
                    img_path = os.path.join(directorio, filename)
                    # Crear una nueva página para cada imagen
                    report.drawImage(img_path, 50, 150, width=500, height=400)
                    report.showPage()  # Cerrar la página de la imagen

        # Agregar imágenes desde el directorio principal
        agregar_imagenes_desde_directorio(self.output_dir)

        # Agregar imágenes desde la carpeta "eventos"
        eventos_dir = os.path.join(self.output_dir, "eventos")
        if os.path.exists(eventos_dir):
            agregar_imagenes_desde_directorio(eventos_dir)

            # Agregar imágenes desde la carpeta "individuales" dentro de "eventos"
            individuales_dir = os.path.join(eventos_dir, "individuales")
            if os.path.exists(individuales_dir):
                agregar_imagenes_desde_directorio(individuales_dir)

        # Guardar el reporte
        report.save()
