"""
Distribuidor de Claves
Organiza notas entre chave de Sol (mão direita) e chave de Fá (mão esquerda)
seguindo as regras específicas do sistema hermético
"""

from typing import Dict, List
from .note_generator import Note


class StaffDistributor:
    """
    Distribui notas entre claves seguindo as regras herméticas
    """

    def distribute(self, note_data: Dict, chord_info: Dict) -> Dict:
        """
        Distribui notas entre mãos baseado no tipo de acorde

        Args:
            note_data: Notas geradas pelo NoteGenerator  
            chord_info: Informações do acorde parseado

        Returns:
            Dict: Notas distribuídas por mão
        """
        chord_type = chord_info.get('chord_type', 'maior')
        root_note = chord_info.get('root', 'C')

        # Distribuição baseada no tipo de acorde
        if chord_info.get('has_slash', False):
            distribution = self._distribute_slash_chord(note_data, chord_info)
        elif chord_type == 'maior':
            distribution = self._distribute_major_chord(note_data, root_note)
        elif chord_type == 'menor' and self._is_c_minor_479_pattern(chord_info):
            distribution = self._distribute_c_minor_479_pattern(
                note_data, root_note)
        elif chord_type == 'dominante':
            distribution = self._distribute_dominant_chord(
                note_data, root_note)
        elif chord_type == 'meio-diminuto':
            distribution = self._distribute_meio_diminuto_chord(
                note_data, root_note)
        else:
            # Distribuição padrão para outros tipos
            distribution = self._distribute_default(note_data)

        # Aplicar ajuste de oitava se necessário
        distribution = self._adjust_octave_if_needed(distribution)

        # Garante que as notas em cada mão estejam em ordem ascendente de altura
        if 'left_hand' in distribution:
            distribution['left_hand'] = self._ensure_ascending_pitch(
                distribution['left_hand'])
        if 'right_hand' in distribution:
            distribution['right_hand'] = self._ensure_ascending_pitch(
                distribution['right_hand'])

        return distribution

    def _distribute_slash_chord(self, note_data: Dict, chord_info: Dict) -> Dict:
        """
        Distribui acordes sobrepostos (slash chords)

        Estrutura: ACORDE_SUPERIOR/ACORDE_INFERIOR
        - Mão direita: notas do acorde superior
        - Mão esquerda: notas do acorde inferior (uma oitava abaixo)
        """
        right_hand_notes = note_data.get('right_hand', [])
        left_hand_notes = note_data.get('left_hand', [])

        # Para acordes sobrepostos (slash chords), descer a mão esquerda uma oitava
        # para criar melhor separação entre os acordes superior e inferior
        adjusted_left_hand = []
        for note in left_hand_notes:
            if note.octave > 1:  # Evitar oitavas muito graves (menores que 1)
                lower_note = Note(
                    name=note.name,
                    octave=note.octave - 1,
                    midi_number=note.midi_number - 12,
                    enharmonic=getattr(note, 'enharmonic', note.name)
                )
                adjusted_left_hand.append(lower_note)
            else:
                # Se já estiver muito grave, manter na oitava atual
                adjusted_left_hand.append(note)

        print(f"🎵 Slash chord: mão esquerda descida uma oitava")
        print(
            f"   Original: {[f'{n.name}{n.octave}' for n in left_hand_notes]}")
        print(
            f"   Ajustada: {[f'{n.name}{n.octave}' for n in adjusted_left_hand]}")

        return {
            'left_hand': adjusted_left_hand,
            'right_hand': right_hand_notes
        }

    def _distribute_major_chord(self, note_data: Dict, root_note: str) -> Dict:
        """Distribui acordes maiores"""
        all_notes = note_data['right_hand']

        if not all_notes:
            return self._empty_distribution()

        # Para acordes 7+: fundamental + 5ª na esquerda, resto na direita
        if len(all_notes) >= 6:
            fundamental = None
            fifth = None
            other_notes = []

            for note in all_notes:
                if note.name == root_note:
                    fundamental = note
                elif self._is_perfect_fifth(root_note, note.name):
                    fifth = note
                else:
                    other_notes.append(note)

            bass_notes = []
            if fundamental:
                bass_notes.append(fundamental)
            if fifth:
                bass_notes.append(fifth)

            # Separar terça e outras notas
            third_note = None
            remaining_other_notes = []

            for note in other_notes:
                # Verificar se é a terça do acorde
                if self._is_major_third(note, root_note):
                    third_note = note
                else:
                    remaining_other_notes.append(note)

            # Adicionar terça à mão esquerda
            if third_note:
                bass_notes.append(third_note)

            # Atualizar other_notes para excluir a terça
            other_notes = remaining_other_notes

            # Garantir que a tônica seja sempre a nota mais grave na mão esquerda
            if len(bass_notes) > 1:
                # Ordenar notas da mão esquerda por altura MIDI
                bass_notes_with_midi = [
                    (note, self._note_to_midi(note)) for note in bass_notes]
                bass_notes_with_midi.sort(
                    key=lambda x: x[1])  # Ordenar por MIDI
                bass_notes = [note for note, midi in bass_notes_with_midi]

            # Para acordes maiores com sétima maior (7+), descer mão esquerda uma oitava
            adjusted_bass_notes = []
            for note in bass_notes:
                # Evitar oitavas muito graves (menores que 1)
                if note.octave > 1:
                    lower_note = Note(
                        name=note.name,
                        octave=note.octave - 1,
                        midi_number=note.midi_number - 12,
                        enharmonic=getattr(note, 'enharmonic', note.name)
                    )
                    adjusted_bass_notes.append(lower_note)
                else:
                    adjusted_bass_notes.append(note)

            # Descer a nota mais aguda da mão direita uma oitava
            adjusted_other_notes = []
            if other_notes:
                # Encontrar a nota mais aguda
                highest_note = max(
                    other_notes, key=lambda n: self._note_to_midi(n))

                for note in other_notes:
                    if note == highest_note and note.octave > 2:  # Evitar oitavas muito graves
                        # Descer uma oitava
                        lower_note = Note(
                            name=note.name,
                            octave=note.octave - 1,
                            midi_number=note.midi_number - 12,
                            enharmonic=getattr(note, 'enharmonic', note.name)
                        )
                        adjusted_other_notes.append(lower_note)
                    else:
                        adjusted_other_notes.append(note)
            else:
                adjusted_other_notes = other_notes

            print(f"🎵 Acorde maior com 7+ ajustado:")
            print(
                f"   Mão esquerda (com terça): {[f'{n.name}{n.octave}' for n in adjusted_bass_notes]}")
            print(
                f"   Mão direita (nota aguda -1 oitava): {[f'{n.name}{n.octave}' for n in adjusted_other_notes]}")

            return {
                'left_hand': adjusted_bass_notes,
                'right_hand': adjusted_other_notes
            }
        else:
            # Tríade simples: tudo na direita
            return {
                'left_hand': [],
                'right_hand': all_notes
            }

    def _distribute_c_minor_479_pattern(self, note_data: Dict, root_note: str) -> Dict:
        """Distribuição específica para C-479"""
        all_notes = note_data['right_hand']

        bass_notes = []
        treble_notes = []

        # Mapear nomes de notas para números MIDI (base C = 0)
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        root_val = note_map.get(root_note, 0)
        for note in all_notes:
            note_name = note.name
            val = note_map.get(note_name, -1)
            interval = (val - root_val) % 12

            # Mão esquerda: tônica (0), quarta justa (5), sétima menor (10)
            if interval == 0:
                bass_notes.append(note)
            elif interval == 5:
                bass_notes.append(note)
            elif interval == 10:
                bass_notes.append(note)
            else:
                treble_notes.append(note)

        # Para acordes menores extendidos (X-479), descer mão esquerda uma oitava
        adjusted_bass_notes = []
        for note in bass_notes:
            if note.octave > 1:  # Evitar oitavas muito graves (menores que 1)
                lower_note = Note(
                    name=note.name,
                    octave=note.octave - 1,
                    midi_number=note.midi_number - 12,
                    enharmonic=getattr(note, 'enharmonic', note.name)
                )
                adjusted_bass_notes.append(lower_note)
            else:
                adjusted_bass_notes.append(note)

        return {
            'left_hand': adjusted_bass_notes,
            'right_hand': treble_notes
        }

    def _distribute_dominant_chord(self, note_data: Dict, root_note: str) -> Dict:
        """Distribui acordes dominantes"""
        print(
            f"[staff_distributor] Entrando em _distribute_dominant_chord com root_note={root_note}")
        all_notes = note_data['right_hand']

        if not all_notes:
            print(
                "[staff_distributor] Nenhuma nota encontrada para dominante, retornando distribuição vazia.")
            return self._empty_distribution()

        bass_notes = []
        treble_notes = []

        fundamental = None
        for note in all_notes:
            if note.name == root_note:
                fundamental = note
                print(
                    f"[staff_distributor] Fundamental encontrada: {note.name}{note.octave}")
                break

        if fundamental:
            bass_notes.append(fundamental)

        for note in all_notes:
            if note != fundamental and self._is_perfect_fifth(root_note, note.name):
                bass_notes.append(note)
                print(
                    f"[staff_distributor] Quinta justa encontrada: {note.name}{note.octave}")
                break

        third_note = None
        other_treble_notes = []

        print(f"[staff_distributor] Procurando terça entre as notas restantes...")
        for note in all_notes:
            if note not in bass_notes:
                print(f"   Testando {note.name}{note.octave}...")
                if self._is_major_third(note, root_note) or self._is_minor_third(note, root_note):
                    if third_note is None:
                        third_note = note
                        print(
                            f"   ✅ Encontrada terça: {note.name}{note.octave}")
                    else:
                        other_treble_notes.append(note)
                        print(
                            f"   ⚠️  Terça adicional ignorada: {note.name}{note.octave}")
                else:
                    other_treble_notes.append(note)
                    print(
                        f"   ➕ Adicionada às outras: {note.name}{note.octave}")

        if third_note:
            bass_notes.append(third_note)
            print(
                f"[staff_distributor] Terça {third_note.name}{third_note.octave} adicionada à mão esquerda")
        else:
            print("[staff_distributor] Nenhuma terça encontrada!")

        treble_notes = other_treble_notes

        if len(bass_notes) > 1:
            bass_notes_with_midi = [(note, self._note_to_midi(note))
                                    for note in bass_notes]
            bass_notes_with_midi.sort(key=lambda x: x[1])
            bass_notes = [note for note, midi in bass_notes_with_midi]
            print(
                f"[staff_distributor] Bass notes ordenadas por altura MIDI: {[note.name+str(note.octave) for note in bass_notes]}")

        adjusted_bass_notes = []
        for note in bass_notes:
            if note.octave > 1:
                lower_note = Note(
                    name=note.name,
                    octave=note.octave - 1,
                    midi_number=note.midi_number - 12,
                    enharmonic=getattr(note, 'enharmonic', note.name)
                )
                adjusted_bass_notes.append(lower_note)
                print(
                    f"[staff_distributor] Baixando {note.name}{note.octave} para {lower_note.name}{lower_note.octave}")
            else:
                adjusted_bass_notes.append(note)

        adjusted_treble_notes = []
        if treble_notes:
            highest_note = max(
                treble_notes, key=lambda n: self._note_to_midi(n))
            print(
                f"[staff_distributor] Nota mais aguda da mão direita: {highest_note.name}{highest_note.octave}")
            for note in treble_notes:
                if note == highest_note and note.octave > 2:
                    lower_note = Note(
                        name=note.name,
                        octave=note.octave - 1,
                        midi_number=note.midi_number - 12,
                        enharmonic=getattr(note, 'enharmonic', note.name)
                    )
                    adjusted_treble_notes.append(lower_note)
                    print(
                        f"[staff_distributor] Baixando {note.name}{note.octave} para {lower_note.name}{lower_note.octave}")
                else:
                    adjusted_treble_notes.append(note)
        else:
            adjusted_treble_notes = treble_notes

        print(
            f"[staff_distributor] Distribuição dominante finalizada. Mão esquerda: {[note.name+str(note.octave) for note in adjusted_bass_notes]}, Mão direita: {[note.name+str(note.octave) for note in adjusted_treble_notes]}")
        return {
            'left_hand': adjusted_bass_notes,
            'right_hand': adjusted_treble_notes
        }

    def _distribute_meio_diminuto_chord(self, note_data: Dict, root_note: str) -> Dict:
        """Distribui acordes meio-diminutos garantindo tônica no baixo"""
        print(
            f"[staff_distributor] Entrando em _distribute_meio_diminuto_chord com root_note={root_note}")
        all_notes = note_data['right_hand']

        if not all_notes:
            print(
                "[staff_distributor] Nenhuma nota encontrada para meio-diminuto, retornando distribuição vazia.")
            return self._empty_distribution()

        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        root_val = note_map.get(root_note, 0)
        bass_notes = []
        treble_notes = []

        for note in all_notes:
            note_name = note.name
            val = note_map.get(note_name, -1)
            interval = (val - root_val) % 12

            if interval == 0:
                bass_notes.append(note)
                print(
                    f"[staff_distributor] Tônica encontrada: {note.name}{note.octave}")
            elif interval == 3:
                bass_notes.append(note)
                print(
                    f"[staff_distributor] Terça menor encontrada: {note.name}{note.octave}")
            elif interval == 6:
                bass_notes.append(note)
                print(
                    f"[staff_distributor] Quinta diminuta encontrada: {note.name}{note.octave}")
            else:
                treble_notes.append(note)
                print(
                    f"[staff_distributor] Nota adicionada à mão direita: {note.name}{note.octave}")

        adjusted_bass_notes = []
        for note in bass_notes:
            if note.octave > 1:
                lower_note = Note(
                    name=note.name,
                    octave=note.octave - 1,
                    midi_number=note.midi_number - 12,
                    enharmonic=getattr(note, 'enharmonic', note.name)
                )
                adjusted_bass_notes.append(lower_note)
                print(
                    f"[staff_distributor] Baixando {note.name}{note.octave} para {lower_note.name}{lower_note.octave}")
            else:
                adjusted_bass_notes.append(note)

        print(
            f"[staff_distributor] Distribuição meio-diminuto finalizada. Mão esquerda: {[note.name+str(note.octave) for note in adjusted_bass_notes]}, Mão direita: {[note.name+str(note.octave) for note in treble_notes]}")
        return {
            'left_hand': adjusted_bass_notes,
            'right_hand': treble_notes
        }

        # (Bloco antigo removido, agora a lógica é apenas a nova distribuição)

    def _distribute_default(self, note_data: Dict) -> Dict:
        """Distribuição padrão"""
        all_notes = note_data['right_hand']
        return {
            'left_hand': [],
            'right_hand': all_notes
        }

    def _empty_distribution(self) -> Dict:
        """Retorna distribuição vazia"""
        return {
            'left_hand': [],
            'right_hand': []
        }

    def _is_c_minor_479_pattern(self, chord_info: Dict) -> bool:
        """Verifica se é o padrão X-479 (menor com 4, 7, 9) para qualquer tônica"""
        # Aceita qualquer acorde menor com intervalos 4, 7, 9
        intervals = chord_info.get('right_hand', {}).get('intervals', [])
        # Precisa ser acorde menor e ter exatamente esses intervalos
        chord_type = chord_info.get('chord_type', '')
        return chord_type == 'menor' and set(intervals) == {'4', '7', '9'}

    def _is_perfect_fifth(self, root_name: str, note_name: str) -> bool:
        """Verifica se uma nota é a quinta justa"""
        note_positions = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
            'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        root_pos = note_positions.get(root_name, 0)
        note_pos = note_positions.get(note_name, 0)

        return (note_pos - root_pos) % 12 == 7

    def _create_note_higher_octave(self, note):
        """Cria uma nova nota uma oitava acima"""
        # Usar o mesmo construtor que o NoteGenerator usa
        higher_midi = self._note_to_midi(note) + 12
        return Note(
            name=note.name,
            octave=note.octave + 1,
            midi_number=higher_midi,
            enharmonic=getattr(note, 'enharmonic', note.name)
        )

    def _note_to_midi(self, note) -> int:
        """Converte Note para número MIDI"""
        note_positions = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
            'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        base_midi = note_positions.get(note.name, 0)
        return (note.octave + 1) * 12 + base_midi

    def _adjust_octave_if_needed(self, distribution: Dict) -> Dict:
        """
        Ajusta oitavas se a nota mais aguda ultrapassar B5
        Se isso acontecer, desce todas as notas uma oitava
        """
        all_notes = distribution.get(
            'right_hand', []) + distribution.get('left_hand', [])

        if not all_notes:
            return distribution

        # Encontrar a nota mais aguda
        highest_note = max(
            all_notes, key=lambda note: self._note_to_midi(note))
        highest_midi = self._note_to_midi(highest_note)

        # B5 = 83 em MIDI (B na oitava 5)
        # Se a nota mais aguda for maior que B5, descer todas uma oitava
        if highest_midi > 83:  # Maior que B5
            print(
                f"🎵 Nota mais aguda {highest_note.name}{highest_note.octave} ultrapassa B5, descendo uma oitava...")

            # Descer todas as notas uma oitava
            adjusted_right = []
            for note in distribution.get('right_hand', []):
                if note.octave > 0:  # Evitar oitavas negativas
                    adjusted_note = Note(
                        name=note.name,
                        octave=note.octave - 1,
                        midi_number=note.midi_number - 12,
                        enharmonic=getattr(note, 'enharmonic', note.name)
                    )
                    adjusted_right.append(adjusted_note)
                else:
                    adjusted_right.append(note)

            adjusted_left = []
            for note in distribution.get('left_hand', []):
                if note.octave > 0:  # Evitar oitavas negativas
                    adjusted_note = Note(
                        name=note.name,
                        octave=note.octave - 1,
                        midi_number=note.midi_number - 12,
                        enharmonic=getattr(note, 'enharmonic', note.name)
                    )
                    adjusted_left.append(adjusted_note)
                else:
                    adjusted_left.append(note)

            return {
                'right_hand': adjusted_right,
                'left_hand': adjusted_left
            }

        # Se não ultrapassar B5, retornar distribuição original
        return distribution

    def _is_major_third(self, note, root_note_str):
        """Verifica se a nota é a terça maior em relação à tônica."""
        # Mapear nomes de notas para números MIDI (base C4 = 60)
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        # Obter valores MIDI das notas
        note_midi = note_map.get(note.name, 0)
        root_midi = note_map.get(root_note_str, 0)

        # Calcula o intervalo em semitons
        interval = (note_midi - root_midi) % 12
        return interval == 4

    def _is_minor_third(self, note, root_note_str):
        """Verifica se a nota é a terça menor em relação à tônica."""
        # Mapear nomes de notas para números MIDI (base C4 = 60)
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        # Obter valores MIDI das notas
        note_midi = note_map.get(note.name, 0)
        root_midi = note_map.get(root_note_str, 0)

        # Calcula o intervalo em semitons
        interval = (note_midi - root_midi) % 12
        return interval == 3

    def _ensure_ascending_pitch(self, notes: List[Note]) -> List[Note]:
        """
        Garante que uma lista de notas esteja em ordem ascendente de altura,
        ajustando a oitava conforme necessário.
        """
        if not notes:
            return []

        # A primeira nota serve como referência inicial
        for i in range(1, len(notes)):
            previous_note = notes[i-1]
            current_note = notes[i]

            # Enquanto a nota atual for mais grave ou igual à anterior, sobe a oitava
            while current_note.midi_number <= previous_note.midi_number:
                current_note.octave += 1
                current_note.midi_number += 12  # Atualizar midi_number também!

        return notes

    def distribute_notes(self, notes: List[Note], parsed_data: Dict) -> Dict:
        # ... existing code ...
        # A ordem original dos intervalos na cifra é mais importante, então a ordenação foi desativada.
        # notes.sort(key=lambda n: n.sort_key)

        # ... existing code ...

        # Garante que as notas em cada mão estejam em ordem ascendente de altura
        left_hand_notes = self._ensure_ascending_pitch(left_hand_notes)
        right_hand_notes = self._ensure_ascending_pitch(right_hand_notes)

        return {
            'left_hand': left_hand_notes,
            'right_hand': right_hand_notes,
            'original': parsed_data.get('original', '')
        }
