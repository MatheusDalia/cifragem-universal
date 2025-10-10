"""
Tradutor de Cifras Herméticas do Hermeto Pascoal
Converte o sistema único de cifragem do Hermeto para partitura de piano
"""

from .core.hermeto_translator import HermetoTranslator
from .core.chord_parser import ChordParser
from .core.interval_converter import IntervalConverter
from .core.note_generator import NoteGenerator
from .core.staff_distributor import StaffDistributor
from .core.score_generator import ScoreGenerator

__version__ = "0.1.0"
__author__ = "Matheus Dalia"

__all__ = [
    "HermetoTranslator",
    "ChordParser",
    "IntervalConverter",
    "NoteGenerator",
    "StaffDistributor",
    "ScoreGenerator"
]
