import json
from modelo.senial import SenialAudio
from procesador.procesador import *

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
        
    
    def generate_report(self, senial_audio: SenialAudio, segmenter:Segmenter, filtro_hp:HighPassFilter, filtro_lp:LowPassFilter,  event_processor: EventProcessor):
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