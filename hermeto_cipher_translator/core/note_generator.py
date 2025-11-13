"""
Gerador de Notas Absolutas
Transforma intervalos relativos em notas musicais reais baseado na fundamental
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

from .interval_converter import Interval, IntervalConverter


@dataclass
class Note:
    """Representa uma nota musical com suas propriedades"""
    name: str          # Nome da nota (C, F#, Bb, etc.)
    octave: int        # Oitava da nota
    midi_number: int   # Número MIDI (C4 = 60)
    enharmonic: str    # Enarmônica alternativa se aplicável


class NoteGenerator:
    """
    Gera notas absolutas a partir de intervalos e nota fundamental

    Baseado no sistema cromático temperado, considera enarmônias
    e distribui notas em oitavas apropriadas para piano
    """

    def __init__(self):
        print("[note_generator] Inicializando NoteGenerator...")
        # Inicializar o interval converter
        self.interval_converter = IntervalConverter()

        # Mapeamento de notas para números de semitom (C = 0)
        self.note_to_semitone = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        # Mapeamento reverso: semitom para nomes de nota
        self.semitone_to_note = {
            0: ['C'], 1: ['C#', 'Db'], 2: ['D'], 3: ['D#', 'Eb'],
            4: ['E'], 5: ['F'], 6: ['F#', 'Gb'], 7: ['G'],
            8: ['G#', 'Ab'], 9: ['A'], 10: ['A#', 'Bb'], 11: ['B']
        }

        # Preferências enarmônicas por contexto
        self.enharmonic_preferences = {
            'sharp_keys': ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#'],
            'flat_keys': ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb'],
            'sharp_notes': ['C#', 'D#', 'F#', 'G#', 'A#'],
            'flat_notes': ['Db', 'Eb', 'Gb', 'Ab', 'Bb']
        }

        # Oitavas padrão para claves (uma oitava mais baixa)
        self.default_octaves = {
            'treble': 3,  # Clave de Sol (mão direita) - era 4, agora 3
            'bass': 2     # Clave de Fá (mão esquerda) - era 3, agora 2
        }

    def generate(self, parsed_data: Dict) -> Dict:
        print(
            f"[note_generator] generate: Gerando notas para dados parseados: {parsed_data}")
        """
        Gera notas musicais baseadas nos dados parseados

        Args:
            parsed_data: Dados do acorde parseado

        Returns:
            Dict: Notas organizadas por mão
        """
        if parsed_data.get('has_slash', False):
            print("[note_generator] Detecção de acorde sobreposto (com barra)")
            # Acordes sobrepostos: processar cada parte separadamente
            result = self._generate_slash_chord(parsed_data)
            print(
                f"[note_generator] Notas geradas para acorde sobreposto: {result}")
            return result
        else:
            # Acordes simples: processar como antes
            result = self._generate_regular_chord(parsed_data)
            print(
                f"[note_generator] Notas geradas para acorde regular: {result}")
            return result

    def _generate_slash_chord(self, parsed_data: Dict) -> Dict:
        print(
            f"[note_generator] _generate_slash_chord: Gerando notas para acorde sobreposto: {parsed_data}")
        """
        Gera notas para acordes sobrepostos (slash chords)
        """
        # Converter intervalos usando o interval converter
        intervals_data = self.interval_converter.convert(parsed_data)

        # Gerar notas da mão direita (acorde superior)
        right_hand_notes = []
        if intervals_data.get('right_hand'):
            right_root = parsed_data['right_hand']['root']
            for interval in intervals_data['right_hand']:
                note = self._generate_note_from_interval(
                    right_root, interval, 4)  # Oitava 4 para direita
                if note:
                    right_hand_notes.append(note)

        # Gerar notas da mão esquerda (acorde inferior)
        left_hand_notes = []
        if intervals_data.get('left_hand'):
            left_root = parsed_data['left_hand']['root']

            # Para acordes simples no baixo (como E em Ab7/E), só a fundamental
            if not parsed_data['left_hand'].get('intervals'):
                # Apenas a nota fundamental
                fundamental = self._create_note(
                    left_root, 3, f"{left_root}3")  # Oitava 3 para baixo
                left_hand_notes.append(fundamental)
            else:
                # Sempre incluir a fundamental do acorde inferior primeiro
                fundamental = self._create_note(left_root, 3, f"{left_root}3")
                left_hand_notes.append(fundamental)

                # Gerar intervalos do acorde inferior (REMOVER filtro de duplicatas)
                for interval in intervals_data['left_hand']:
                    if interval.degree != 1:  # Não duplicar fundamental
                        note = self._generate_note_from_interval(
                            left_root, interval, 3)  # Oitava 3 para esquerda
                        if note:
                            # ACEITAR TODAS as notas - não filtrar duplicatas
                            left_hand_notes.append(note)

        return {
            'left_hand': left_hand_notes,
            'right_hand': right_hand_notes
        }

    def _generate_regular_chord(self, parsed_data: Dict) -> Dict:
        print(
            f"[note_generator] _generate_regular_chord: Gerando notas para acorde regular: {parsed_data}")
        """
        Gera notas para acordes regulares (não sobrepostos)
        """
        # Converter intervalos
        intervals_data = self.interval_converter.convert(parsed_data)
        notes = []

        root_note = parsed_data['root']

        if 'right_hand' in intervals_data and intervals_data['right_hand']:
            intervals = intervals_data['right_hand']
        elif 'all_intervals' in intervals_data:
            intervals = intervals_data['all_intervals']
        else:
            intervals = []

        for interval in intervals:
            note = self._generate_note_from_interval(root_note, interval, 4)
            if note:
                notes.append(note)

        return {
            'left_hand': [],
            'right_hand': notes
        }

    def _generate_note_from_interval(self, root_note: str, interval, default_octave: int):
        print(
            f"[note_generator] _generate_note_from_interval: Gerando nota a partir de root '{root_note}', intervalo '{interval}', oitava padrão {default_octave}")
        """
        Gera uma nota a partir de um intervalo
        """
        if hasattr(interval, 'semitones'):
            # É um objeto Interval
            semitones = interval.semitones
        else:
            # É uma string, converter
            return None

        # Calcular nota alvo
        root_semitone = self.note_to_semitone[root_note]
        target_semitone = (root_semitone + semitones) % 12
        # Priorizar bemol se root_note for bemol
        note_names = self.semitone_to_note[target_semitone]
        # Se root_note tem 'b' (bemol), sempre priorize bemol
        if 'b' in root_note and len(note_names) > 1:
            # Se houver bemol disponível, escolha sempre o bemol
            target_note_name = next(
                (n for n in note_names if 'b' in n), note_names[-1])
        elif 'b' in root_note:
            # Se root_note tem 'b' mas não há bemol disponível, mantenha o nome padrão
            target_note_name = note_names[-1]
        else:
            # Caso contrário, escolha o primeiro nome (padrão)
            target_note_name = note_names[0]

        # Calcular oitava corretamente
        octave_adjustment = (root_semitone + semitones) // 12
        final_octave = default_octave + octave_adjustment

        # Garantir oitavas mínimas
        if final_octave < 2:
            final_octave = 2 if default_octave <= 3 else 4

        return self._create_note(target_note_name, final_octave, f"{target_note_name}{final_octave}")

    def _create_note(self, name: str, octave: int, full_name: str) -> Note:
        print(
            f"[note_generator] _create_note: Criando nota '{name}' na oitava {octave} (nome completo: {full_name})")
        """Cria um objeto Note"""
        midi_number = (octave + 1) * 12 + self.note_to_semitone[name]
        enharmonic = name  # Simplificado por agora

        return Note(
            name=name,
            octave=octave,
            midi_number=midi_number,
            enharmonic=enharmonic
        )

    def _midi_to_note_name(self, midi_value: int) -> str:
        print(
            f"[note_generator] _midi_to_note_name: Convertendo valor MIDI {midi_value} para nome de nota")
        """Converte valor MIDI para nome da nota"""
        semitone = midi_value % 12
        return self.semitone_to_note[semitone][0]  # Primeira opção
