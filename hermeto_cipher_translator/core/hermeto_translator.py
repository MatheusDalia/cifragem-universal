"""
Módulo principal do tradutor de cifras herméticas
Orquestra todos os componentes para realizar a tradução completa
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Import condicional do music21
try:
    from music21 import stream, note, pitch, interval, duration, meter
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    # Mock classes para desenvolvimento sem music21

    class stream:
        class Score:
            pass

from .chord_parser import ChordParser
from .interval_converter import IntervalConverter
from .note_generator import NoteGenerator
from .staff_distributor import StaffDistributor
from .score_generator import ScoreGenerator


@dataclass
class HermetoChord:
    """Representa um acorde hermético completo após processamento"""
    original_cipher: str
    left_hand_notes: List[str]  # Notas para clave de Fá (mão esquerda)
    right_hand_notes: List[str]  # Notas para clave de Sol (mão direita)
    chord_type: str  # maior, menor, dominante, suspenso, meio-diminuto, sobreposto
    intervals: List[str]  # Intervalos identificados


class HermetoTranslator:
    """
    Classe principal que coordena toda a tradução de cifras herméticas
    """

    def __init__(self):
        self.parser = ChordParser()
        self.interval_converter = IntervalConverter()
        self.note_generator = NoteGenerator()
        self.staff_distributor = StaffDistributor()
        self.score_generator = ScoreGenerator()

    def translate(self, cipher: str):
        """
        Traduz uma cifra hermética completa para partitura de piano

        Args:
            cipher: String da cifra hermética (ex: "C458/A5+7")

        Returns:
            Score object (music21.stream.Score se disponível)
        """
        # 1. Parse da cifra
        parsed_data = self.parser.parse(cipher)

        # 2. Conversão de símbolos para intervalos
        intervals = self.interval_converter.convert(parsed_data)

        # 3. Geração de notas absolutas - CORRIGIR: só passar parsed_data
        notes = self.note_generator.generate(parsed_data)

        # 4. Distribuição nas claves
        staff_notes = self.staff_distributor.distribute(notes, parsed_data)

        # 5. Geração da partitura final
        score = self.score_generator.create_score(staff_notes)

        return score

    def translate_to_hermeto_chord(self, cipher: str) -> HermetoChord:
        """
        Traduz cifra para objeto HermetoChord com informações detalhadas

        Args:
            cipher: String da cifra hermética

        Returns:
            HermetoChord: Objeto com informações completas do acorde
        """
        # Parse completo
        parsed_data = self.parser.parse(cipher)
        intervals = self.interval_converter.convert(parsed_data)

        # CORRIGIR: só passar parsed_data
        notes = self.note_generator.generate(parsed_data)
        staff_notes = self.staff_distributor.distribute(notes, parsed_data)

        return HermetoChord(
            original_cipher=cipher,
            left_hand_notes=staff_notes['left_hand'],
            right_hand_notes=staff_notes['right_hand'],
            chord_type=parsed_data['chord_type'],
            intervals=intervals['all_intervals']
        )

    def batch_translate(self, ciphers: List[str]) -> List:
        """
        Traduz múltiplas cifras de uma vez

        Args:
            ciphers: Lista de cifras herméticas

        Returns:
            List: Lista de partituras traduzidas
        """
        return [self.translate(cipher) for cipher in ciphers]

    def get_chord_info(self, cipher: str) -> Dict:
        """
        Retorna informações detalhadas sobre uma cifra sem gerar partitura

        Args:
            cipher: String da cifra hermética

        Returns:
            Dict: Informações estruturadas sobre o acorde
        """
        hermeto_chord = self.translate_to_hermeto_chord(cipher)

        # Converter objetos Note em dicionários para JSON
        def note_to_dict(note):
            return {
                'name': note.name,
                'octave': note.octave,
                'midi_number': note.midi_number,
                'enharmonic': note.enharmonic
            }

        return {
            'original': hermeto_chord.original_cipher,
            'type': hermeto_chord.chord_type,
            'left_hand': [note_to_dict(note) for note in hermeto_chord.left_hand_notes],
            'right_hand': [note_to_dict(note) for note in hermeto_chord.right_hand_notes],
            'intervals': [{'name': interval.name, 'semitones': interval.semitones, 'degree': interval.degree} for interval in hermeto_chord.intervals],
            'total_notes': len(hermeto_chord.left_hand_notes) + len(hermeto_chord.right_hand_notes)
        }
