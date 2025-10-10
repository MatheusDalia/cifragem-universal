"""
Extensão do sistema de progressões com funcionalidades tonais avançadas
"""

from typing import Dict, List, Tuple
import re


class HermetoTonalProcessor:
    """
    Extensão para processamento tonal avançado das progressões
    """

    def __init__(self):
        # Mapeamento cromático (semitons)
        self.chromatic_notes = [
            'C', 'C#', 'D', 'D#', 'E', 'F',
            'F#', 'G', 'G#', 'A', 'A#', 'B'
        ]

        # Equivalências enarmônicas
        self.enharmonic_map = {
            'C#': 'Db', 'Db': 'C#',
            'D#': 'Eb', 'Eb': 'D#',
            'F#': 'Gb', 'Gb': 'F#',
            'G#': 'Ab', 'Ab': 'G#',
            'A#': 'Bb', 'Bb': 'A#'
        }

        # Escalas maiores (pattern de tons e semitons)
        self.major_scale_pattern = [2, 2, 1, 2, 2, 2, 1]  # Tons/Semitons

        # Graus harmônicos romanos
        self.roman_numerals = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']

    def transpose_chord_symbol(self, chord_symbol: str, semitones: int) -> str:
        """
        Transpõe um símbolo de acorde por número de semitons

        Args:
            chord_symbol: Símbolo do acorde (ex: "Am7", "F#79+13-")
            semitones: Número de semitons para transpor (+/-)

        Returns:
            Símbolo transposto
        """
        # Extrair nota fundamental
        root_match = re.match(r'^([A-G][#b]?)', chord_symbol)
        if not root_match:
            return chord_symbol  # Não conseguiu identificar a fundamental

        root_note = root_match.group(1)
        chord_suffix = chord_symbol[len(root_note):]

        # Transpor a fundamental
        transposed_root = self.transpose_note(root_note, semitones)

        # Verificar se há slash chord (acorde sobre baixo)
        if '/' in chord_suffix:
            parts = chord_suffix.split('/')
            main_part = parts[0]
            bass_part = parts[1]

            # Extrair nota do baixo
            bass_match = re.match(r'^([A-G][#b]?)', bass_part)
            if bass_match:
                bass_note = bass_match.group(1)
                bass_suffix = bass_part[len(bass_note):]

                # Transpor baixo
                transposed_bass = self.transpose_note(bass_note, semitones)
                chord_suffix = f"{main_part}/{transposed_bass}{bass_suffix}"

        return f"{transposed_root}{chord_suffix}"

    def transpose_note(self, note: str, semitones: int) -> str:
        """
        Transpõe uma nota por número de semitons
        """
        # Normalizar nota (usar sustenidos por padrão)
        if note in self.enharmonic_map:
            note = self.enharmonic_map.get(note, note)

        try:
            current_index = self.chromatic_notes.index(note)
        except ValueError:
            # Tentar com enarmônica
            if note in self.enharmonic_map.values():
                enharmonic = [
                    k for k, v in self.enharmonic_map.items() if v == note][0]
                current_index = self.chromatic_notes.index(enharmonic)
            else:
                return note  # Não conseguiu transpor

        # Calcular nova posição
        new_index = (current_index + semitones) % 12
        return self.chromatic_notes[new_index]

    def transpose_progression(self, progression_str: str,
                              from_key: str, to_key: str) -> str:
        """
        Transpõe uma progressão inteira de uma tonalidade para outra

        Args:
            progression_str: Progressão original ("Am7 | C7+ | F")
            from_key: Tonalidade original ("C", "Am", etc.)
            to_key: Tonalidade de destino ("D", "Bm", etc.)

        Returns:
            Progressão transposta
        """
        # Calcular intervalo de transposição
        from_note = re.match(r'^([A-G][#b]?)', from_key).group(1)
        to_note = re.match(r'^([A-G][#b]?)', to_key).group(1)

        from_index = self.chromatic_notes.index(from_note)
        to_index = self.chromatic_notes.index(to_note)

        semitones = (to_index - from_index) % 12

        # Extrair acordes da progressão
        chord_separators = ['|', '/', ' ']
        chords = []

        # Split por diferentes separadores
        current_progression = progression_str
        for sep in chord_separators:
            if sep in current_progression:
                chords = [chord.strip()
                          for chord in current_progression.split(sep)]
                break
        else:
            # Se não encontrou separadores, assumir espaços
            chords = current_progression.split()

        # Transpor cada acorde
        transposed_chords = []
        for chord in chords:
            if chord.strip():
                transposed_chord = self.transpose_chord_symbol(
                    chord.strip(), semitones)
                transposed_chords.append(transposed_chord)

        # Reconstruir progressão (usar | como separador padrão)
        return ' | '.join(transposed_chords)

    def analyze_harmonic_function(self, progression_str: str, key: str) -> List[Dict]:
        """
        Analisa função harmônica dos acordes na tonalidade
        """
        # Construir escala da tonalidade
        key_note = re.match(r'^([A-G][#b]?)', key).group(1)
        is_minor = 'm' in key.lower()

        # Para simplificar, vamos fazer análise básica
        chord_separators = ['|', '/', ' ']
        chords = []

        current_progression = progression_str
        for sep in chord_separators:
            if sep in current_progression:
                chords = [chord.strip()
                          for chord in current_progression.split(sep)]
                break
        else:
            chords = current_progression.split()

        analysis = []
        for chord in chords:
            if not chord.strip():
                continue

            # Extrair fundamental do acorde
            root_match = re.match(r'^([A-G][#b]?)', chord.strip())
            if root_match:
                chord_root = root_match.group(1)

                # Calcular grau na tonalidade
                key_index = self.chromatic_notes.index(key_note)
                chord_index = self.chromatic_notes.index(chord_root)

                interval = (chord_index - key_index) % 12

                # Mapear para grau (simplificado)
                degree_map = {
                    0: 'I',    # Tônica
                    2: 'ii',   # Supertônica
                    4: 'iii',  # Mediante
                    5: 'IV',   # Subdominante
                    7: 'V',    # Dominante
                    9: 'vi',   # Superdominante
                    11: 'vii°'  # Sensível
                }

                degree = degree_map.get(interval, f'#{interval}')

                analysis.append({
                    'chord': chord.strip(),
                    'root': chord_root,
                    'degree': degree,
                    'interval_from_key': interval,
                    'function': self._get_harmonic_function(degree)
                })

        return analysis

    def _get_harmonic_function(self, degree: str) -> str:
        """
        Retorna função harmônica baseada no grau
        """
        function_map = {
            'I': 'Tônica',
            'ii': 'Subdominante',
            'iii': 'Tônica',
            'IV': 'Subdominante',
            'V': 'Dominante',
            'vi': 'Tônica',
            'vii°': 'Dominante'
        }

        return function_map.get(degree, 'Cromática')

    def suggest_chord_substitutions(self, chord: str, key: str) -> List[str]:
        """
        Sugere substituições harmônicas para um acorde
        """
        substitutions = []

        # Análise básica do acorde atual
        analysis = self.analyze_harmonic_function(chord, key)
        if not analysis:
            return substitutions

        current_function = analysis[0]['function']

        # Sugestões baseadas na função
        if current_function == 'Tônica':
            substitutions.extend(['vi', 'iii'])  # Relativos
        elif current_function == 'Dominante':
            substitutions.extend(['vii°', 'iii'])  # Substitutos de dominante
        elif current_function == 'Subdominante':
            substitutions.extend(['ii', 'vi'])  # Substitutos de subdominante

        return substitutions


# Função de conveniência para transposição rápida
def transpose_progression_quick(progression: str, from_key: str, to_key: str) -> str:
    """
    Função rápida para transpor progressão

    Exemplo:
        transpose_progression_quick("Am7 | C7+ | F", "C", "D")
        # Retorna: "Bm7 | D7+ | G"
    """
    processor = HermetoTonalProcessor()
    return processor.transpose_progression(progression, from_key, to_key)


if __name__ == "__main__":
    # Demonstração
    processor = HermetoTonalProcessor()

    print("🎵 DEMONSTRAÇÃO - PROCESSAMENTO TONAL")
    print("=" * 50)

    # Teste de transposição
    original = "Am7 | C7+ | F#79+13- | D7+9+11+"
    print(f"Progressão original: {original}")

    transposta_D = processor.transpose_progression(original, "C", "D")
    print(f"Transposta para Ré: {transposta_D}")

    transposta_F = processor.transpose_progression(original, "C", "F")
    print(f"Transposta para Fá: {transposta_F}")

    # Análise harmônica
    print(f"\n📊 Análise harmônica em Dó maior:")
    analysis = processor.analyze_harmonic_function(original, "C")
    for item in analysis:
        print(f"  {item['chord']} = {item['degree']} ({item['function']})")
