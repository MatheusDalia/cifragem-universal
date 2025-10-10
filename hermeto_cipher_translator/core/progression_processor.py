"""
Módulo para processamento de progressões harmônicas completas
Permite input de sequências de acordes e geração de partituras completas
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from music21 import stream, note, chord, duration, meter, tempo, key, metadata, expressions, harmony

from .hermeto_translator import HermetoTranslator, HermetoChord


@dataclass
class ProgressionChord:
    """Representa um acorde em uma progressão com informações de tempo"""
    hermeto_chord: HermetoChord
    original_symbol: str  # Cifra original exatamente como digitada
    beats: float = 4.0  # duração em beats
    bar_number: int = 1
    beat_position: float = 1.0


class HermetoProgressionProcessor:
    """
    Processa progressões harmônicas completas do sistema hermético
    """

    def __init__(self):
        self.translator = HermetoTranslator()
        self.default_time_signature = "4/4"
        self.default_tempo = 120
        self.default_key = "C"

    def _get_beats_per_measure(self, time_signature: str) -> float:
        """
        Calcula quantos beats há por compasso baseado na fórmula de compasso.

        Exemplos:
        - "4/4" -> 4.0 beats
        - "3/4" -> 3.0 beats  
        - "6/8" -> 6.0 beats (ou 2.0 em compound time, mas simplificando)
        - "12/8" -> 12.0 beats
        - "5/4" -> 5.0 beats
        """
        try:
            numerator, denominator = time_signature.split('/')
            numerator = int(numerator)
            denominator = int(denominator)

            # Para simplicidade, tratamos o numerador como número de beats
            # Em casos mais complexos como 6/8, seria preciso lógica adicional
            return float(numerator)
        except:
            # Fallback para 4/4 se não conseguir parsear
            return 4.0

    def parse_progression_string(self, progression_str: str, time_signature: str = "4/4") -> List[Dict]:
        """
        Parseia string de progressão em diversos formatos:

        FORMATOS BÁSICOS:
        - "Am7 | C7+ | F#79+13-" (um acorde por compasso, separados por |)
        - "Am7 C7+ F#79+13-" (um acorde por compasso, separados por espaço)

        MÚLTIPLOS ACORDES POR COMPASSO:
        - "Am7(2) C7+(2)" (2 acordes de 2 beats cada = 1 compasso 4/4)
        - "Am7 C7+ Dm7 G7" (4 acordes de 1 beat cada = 1 compasso 4/4)
        - "Am7(3) C7+(1)" (Am7=3 beats, C7+=1 beat = 1 compasso)
        - "Am7(1) C7+(1) Dm7(1) G7(1) | F7+(4)" (compasso 1: 4 acordes, compasso 2: 1 acorde)

        SEPARAÇÃO POR COMPASSO:
        - "Am7 / C7+" (separação explícita por compasso com /)

        DURAÇÕES:
        - Sem parênteses: duração automática (4 beats se único, distribuído se múltiplos)
        - Com parênteses: duração específica em beats - "Am7(2)" = 2 beats
        """

        # Limpar string
        progression_str = progression_str.strip()
        beats_per_measure = self._get_beats_per_measure(time_signature)

        # Detectar separadores
        if '|' in progression_str:
            # Formato com | - cada parte pode ter múltiplos acordes
            measure_parts = [part.strip()
                             for part in progression_str.split('|')]
            chord_parts = []
            for measure in measure_parts:
                if ' ' in measure:
                    # Múltiplos acordes neste compasso
                    measure_chords = measure.split()
                    chord_parts.extend(
                        self._distribute_chords_in_measure(measure_chords, beats_per_measure))
                else:
                    chord_parts.append(measure)
        elif '/' in progression_str:
            # Formato com / (separação por compasso)
            chord_parts = [part.strip() for part in progression_str.split('/')]
        else:
            # Formato com espaços - precisa determinar se são múltiplos por compasso
            space_parts = progression_str.split()
            chord_parts = self._distribute_chords_in_measure(
                space_parts, beats_per_measure)

        parsed_chords = []
        current_bar = 1
        current_beat = 1.0

        for i, chord_part in enumerate(chord_parts):
            chord_part = chord_part.strip()
            if not chord_part:
                continue

            # Extrair duração se especificada: "Am7(2)"
            duration_match = re.search(r'\((\d+(?:\.\d+)?)\)', chord_part)
            if duration_match:
                chord_duration = float(duration_match.group(1))
                chord_symbol = re.sub(
                    r'\(\d+(?:\.\d+)?\)', '', chord_part).strip()
            else:
                chord_duration = beats_per_measure  # duração padrão baseada no compasso
                chord_symbol = chord_part

            parsed_chords.append({
                'symbol': chord_symbol,
                'duration': chord_duration,
                'bar': current_bar,
                'beat': current_beat
            })

            # Calcular próxima posição
            current_beat += chord_duration
            if current_beat > beats_per_measure:
                current_bar += 1
                current_beat = 1.0

        return parsed_chords

    def _distribute_chords_in_measure(self, chord_list: List[str], beats_per_measure: float = 4.0) -> List[str]:
        """
        Distribui acordes automaticamente em um compasso.
        Se não tiverem duração específica, divide igualmente o compasso.

        Args:
            chord_list: Lista de acordes
            beats_per_measure: Número de beats por compasso (ex: 4.0 para 4/4, 3.0 para 3/4)
        """
        result = []

        for chord in chord_list:
            chord = chord.strip()
            if not chord:
                continue

            # Se já tem duração especificada, manter
            if re.search(r'\(\d+(?:\.\d+)?\)', chord):
                result.append(chord)
            else:
                # Calcular duração automática baseada no número de acordes e tipo de compasso
                num_chords = len([c for c in chord_list if c.strip()])
                # Dividir beats do compasso igualmente
                auto_duration = beats_per_measure / num_chords

                # Adicionar duração ao acorde
                result.append(f"{chord}({auto_duration})")

        return result

    def process_progression(self, progression_str: str,
                            time_signature: str = "4/4",
                            tempo_bpm: int = 120,
                            key_signature: str = "C") -> List[ProgressionChord]:
        """
        Processa progressão completa retornando lista de ProgressionChords
        """
        parsed_chords = self.parse_progression_string(
            progression_str, time_signature)
        progression_chords = []

        for chord_info in parsed_chords:
            try:
                # Traduzir cada acorde
                hermeto_chord = self.translator.translate_to_hermeto_chord(
                    chord_info['symbol']
                )

                # Criar ProgressionChord
                prog_chord = ProgressionChord(
                    hermeto_chord=hermeto_chord,
                    # Preservar exatamente como digitado
                    original_symbol=chord_info['symbol'],
                    beats=chord_info['duration'],
                    bar_number=chord_info['bar'],
                    beat_position=chord_info['beat']
                )

                progression_chords.append(prog_chord)

            except Exception as e:
                print(
                    f"Erro ao processar acorde '{chord_info['symbol']}': {e}")
                continue

        return progression_chords

    def generate_musicxml_progression(self, progression_str: str,
                                      time_signature: str = "4/4",
                                      tempo_bpm: int = 120,
                                      key_signature: str = "C",
                                      title: str = "Progressão Hermética",
                                      show_chord_symbols: bool = True) -> stream.Score:
        """
        Gera partitura MusicXML completa para uma progressão
        """
        progression_chords = self.process_progression(
            progression_str, time_signature, tempo_bpm, key_signature
        )

        if not progression_chords:
            raise ValueError("Nenhum acorde válido encontrado na progressão")

        # Criar score
        score = stream.Score()

        # Metadados
        score.append(metadata.Metadata())
        score.metadata.title = title
        score.metadata.composer = 'Sistema Hermético - Hermeto Pascoal'

        # Configurações globais
        tempo_indication = tempo.TempoIndication(
            quarterLength=1, bpm=tempo_bpm)
        score.append(tempo_indication)
        score.append(key.Key(key_signature))
        score.append(meter.TimeSignature(time_signature))

        # Criar partes (mão esquerda e direita)
        right_hand_part = stream.Part()
        right_hand_part.partName = "Mão Direita (Clave de Sol)"
        right_hand_part.append(meter.TimeSignature(time_signature))

        left_hand_part = stream.Part()
        left_hand_part.partName = "Mão Esquerda (Clave de Fá)"
        left_hand_part.append(meter.TimeSignature(time_signature))

        # Processar cada acorde da progressão
        for prog_chord in progression_chords:
            chord_duration = duration.Duration(quarterLength=prog_chord.beats)

            # Adicionar símbolo de cifra no início do acorde (se habilitado)
            if show_chord_symbols:
                # Usar TextExpression simples para cifras herméticas
                chord_text = expressions.TextExpression(
                    prog_chord.original_symbol)
                chord_text.placement = 'above'
                chord_text.quarterLength = 0  # Não ocupa tempo musical
                right_hand_part.append(chord_text)

            # Mão direita
            if prog_chord.hermeto_chord.right_hand_notes:
                right_notes = []
                for note_obj in prog_chord.hermeto_chord.right_hand_notes:
                    music21_note = note.Note(
                        pitch=f"{note_obj.name}{note_obj.octave}",
                        quarterLength=prog_chord.beats
                    )
                    right_notes.append(music21_note)

                if len(right_notes) == 1:
                    right_element = right_notes[0]
                    right_hand_part.append(right_element)
                else:
                    right_element = chord.Chord(
                        right_notes, quarterLength=prog_chord.beats)
                    right_hand_part.append(right_element)
            else:
                # Pausa se não há notas
                rest = note.Rest(quarterLength=prog_chord.beats)
                right_hand_part.append(rest)            # Mão esquerda
            if prog_chord.hermeto_chord.left_hand_notes:
                left_notes = []
                for note_obj in prog_chord.hermeto_chord.left_hand_notes:
                    music21_note = note.Note(
                        pitch=f"{note_obj.name}{note_obj.octave}",
                        quarterLength=prog_chord.beats
                    )
                    left_notes.append(music21_note)

                if len(left_notes) == 1:
                    left_hand_part.append(left_notes[0])
                else:
                    left_chord = chord.Chord(
                        left_notes, quarterLength=prog_chord.beats)
                    left_hand_part.append(left_chord)
            else:
                # Pausa se não há notas
                rest = note.Rest(quarterLength=prog_chord.beats)
                left_hand_part.append(rest)

        # Adicionar partes ao score
        score.append(right_hand_part)
        score.append(left_hand_part)

        return score

    def export_progression_xml(self, progression_str: str,
                               filename: str = "progressao_hermetica.xml",
                               show_chord_symbols: bool = True,
                               **kwargs) -> str:
        """
        Exporta progressão diretamente para arquivo MusicXML

        Args:
            progression_str: String da progressão
            filename: Nome do arquivo de saída
            show_chord_symbols: Se True, adiciona cifras como texto na partitura
            **kwargs: Outros parâmetros (tempo_bpm, key_signature, etc.)
        """
        score = self.generate_musicxml_progression(
            progression_str,
            show_chord_symbols=show_chord_symbols,
            **kwargs
        )

        # Salvar arquivo
        score.write('musicxml', fp=filename)

        return filename

    def export_progression_midi(self, progression_str: str,
                                filename: str = "progressao_hermetica.mid",
                                show_chord_symbols: bool = False,
                                **kwargs) -> str:
        """
        Exporta progressão para arquivo MIDI

        Note: MIDI não suporta texto, então show_chord_symbols é ignorado
        """
        score = self.generate_musicxml_progression(
            progression_str,
            show_chord_symbols=False,  # MIDI não suporta texto
            **kwargs
        )

        # Salvar MIDI
        score.write('midi', fp=filename)

        return filename

    def analyze_progression(self, progression_str: str) -> Dict:
        """
        Analisa progressão harmônica retornando estatísticas
        """
        progression_chords = self.process_progression(progression_str)

        if not progression_chords:
            return {}

        # Análise básica
        chord_types = {}
        total_duration = 0
        chord_symbols = []

        for prog_chord in progression_chords:
            chord_type = prog_chord.hermeto_chord.chord_type
            chord_types[chord_type] = chord_types.get(chord_type, 0) + 1
            total_duration += prog_chord.beats
            chord_symbols.append(prog_chord.hermeto_chord.original_cipher)

        # Calcular estatísticas
        num_chords = len(progression_chords)
        avg_duration = total_duration / num_chords if num_chords > 0 else 0

        # Detectar tonalidade (simplificado)
        # TODO: Implementar análise tonal mais sofisticada

        analysis = {
            'total_acordes': num_chords,
            'duracao_total_beats': total_duration,
            'duracao_media_por_acorde': avg_duration,
            'tipos_acordes': chord_types,
            'sequencia_acordes': chord_symbols,
            'complexidade_media': self._calculate_complexity(progression_chords)
        }

        return analysis

    def _calculate_complexity(self, progression_chords: List[ProgressionChord]) -> float:
        """
        Calcula complexidade média da progressão
        """
        if not progression_chords:
            return 0.0

        total_complexity = 0

        for prog_chord in progression_chords:
            # Complexidade baseada no tipo de acorde
            chord_type = prog_chord.hermeto_chord.chord_type
            complexity = 1.0  # base

            if chord_type == 'dominante':
                complexity += 1.0
            elif chord_type == 'meio-diminuto':
                complexity += 1.5
            elif chord_type == 'sobreposto':
                complexity += 2.0

            # Complexidade baseada no número de notas
            total_notes = (len(prog_chord.hermeto_chord.left_hand_notes) +
                           len(prog_chord.hermeto_chord.right_hand_notes))
            complexity += total_notes * 0.2

            total_complexity += complexity

        return total_complexity / len(progression_chords)


# Função de conveniência para uso rápido
def process_progression(progression_str: str, export_format: str = 'xml',
                        filename: str = None, **kwargs) -> str:
    """
    Função de conveniência para processar progressão rapidamente

    Args:
        progression_str: String da progressão (ex: "Am7 | C7+ | F#79+13-")
        export_format: 'xml', 'midi', ou 'both'
        filename: Nome do arquivo (sem extensão)
        **kwargs: Argumentos adicionais (tempo, time_signature, etc.)

    Returns:
        Nome do arquivo gerado
    """
    processor = HermetoProgressionProcessor()

    if filename is None:
        filename = "progressao_hermetica"

    if export_format.lower() == 'xml':
        return processor.export_progression_xml(progression_str, f"{filename}.xml", **kwargs)
    elif export_format.lower() == 'midi':
        return processor.export_progression_midi(progression_str, f"{filename}.mid", **kwargs)
    elif export_format.lower() == 'both':
        xml_file = processor.export_progression_xml(
            progression_str, f"{filename}.xml", **kwargs)
        midi_file = processor.export_progression_midi(
            progression_str, f"{filename}.mid", **kwargs)
        return f"Gerados: {xml_file} e {midi_file}"
    else:
        raise ValueError("Formato deve ser 'xml', 'midi' ou 'both'")


def demo_multiplos_acordes():
    """
    Demonstra diferentes formas de colocar múltiplos acordes por compasso
    """
    processor = HermetoProgressionProcessor()

    print("🎵 DEMONSTRAÇÃO: MÚLTIPLOS ACORDES POR COMPASSO\n")

    exemplos = [
        # Exemplo 1: 2 acordes de 2 beats cada
        ("Am7(2) C7+(2)", "2 acordes de 2 beats cada = 1 compasso"),

        # Exemplo 2: 4 acordes de 1 beat cada (automático)
        ("Am7 C7+ Dm7 G7", "4 acordes distribuídos automaticamente = 1 compasso"),

        # Exemplo 3: Durações mistas
        ("Am7(3) C7+(1)", "Am7=3 beats, C7+=1 beat = 1 compasso"),

        # Exemplo 4: Múltiplos compassos com diferentes subdivisões
        ("Am7(2) C7+(2) | Dm7 G7 F7+ Em7",
         "Compasso 1: 2+2 beats, Compasso 2: 4 acordes automáticos"),

        # Exemplo 5: Mistura de compassos simples e compostos
        ("C7+(4) | Am7(1) Dm7(1) G7(2) | F7+",
         "Compasso 1: 1 acorde, Compasso 2: 3 acordes, Compasso 3: 1 acorde")
    ]

    for i, (progressao, descricao) in enumerate(exemplos, 1):
        print(f"📝 EXEMPLO {i}: {descricao}")
        print(f"   Input: {progressao}")

        try:
            resultado = processor.process_progression(progressao)
            print(f"   ✅ {len(resultado)} acordes processados:")

            for chord in resultado:
                print(f"      • {chord.hermeto_chord.original_cipher}: {chord.beats} beats "
                      f"(compasso {chord.bar_number}, beat {chord.beat_position})")

            # Calcular total de compassos
            max_bar = max(chord.bar_number for chord in resultado)
            print(f"   📊 Total: {max_bar} compasso(s)")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

        print()


if __name__ == "__main__":
    # Executar demonstração
    demo_multiplos_acordes()

    print("\n" + "="*60)
    print("🎵 EXEMPLO PRÁTICO COMPLETO")
    print("="*60)

    # Exemplo de uso completo
    processor = HermetoProgressionProcessor()

    # Progressão com múltiplos acordes por compasso
    progressao = "Am7(2) C7+(2) | Dm7 G7 F7+ Em7 | D7+9+11+(4)"

    print(f"Progressão: {progressao}")

    # Processar
    resultado = processor.process_progression(progressao)
    print(f"\n✅ {len(resultado)} acordes processados:")

    for i, chord in enumerate(resultado, 1):
        print(f"  {i}. {chord.hermeto_chord.original_cipher} - "
              f"{chord.beats} beats (compasso {chord.bar_number})")

    # Gerar MusicXML
    try:
        xml_file = processor.export_progression_xml(
            progressao,
            "exemplo_multiplos_acordes.xml",
            title="Múltiplos Acordes por Compasso",
            tempo_bpm=100
        )
        print(f"\n✅ Arquivo gerado: {xml_file}")
    except Exception as e:
        print(f"\n❌ Erro na geração: {e}")
