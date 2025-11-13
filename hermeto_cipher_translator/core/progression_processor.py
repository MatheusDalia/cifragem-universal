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
        print("[progression_processor] Inicializando HermetoProgressionProcessor...")
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
        print(
            f"[progression_processor] Calculando beats por compasso para {time_signature}")
        try:
            numerator, denominator = time_signature.split('/')
            numerator = int(numerator)
            denominator = int(denominator)
            return float(numerator)
        except Exception as e:
            print(
                f"[progression_processor] Erro ao parsear time_signature: {e}, usando 4/4")
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
        print(
            f"[progression_processor] Parseando string de progressão: '{progression_str}' com time_signature={time_signature}")
        progression_str = progression_str.strip()
        beats_per_measure = self._get_beats_per_measure(time_signature)

        if '|' in progression_str:
            measure_parts = [part.strip()
                             for part in progression_str.split('|')]
            chord_parts = []
            for measure in measure_parts:
                if ' ' in measure:
                    measure_chords = measure.split()
                    chord_parts.extend(self._distribute_chords_in_measure(
                        measure_chords, beats_per_measure))
                else:
                    chord_parts.append(measure)
        elif '/' in progression_str:
            chord_parts = [part.strip() for part in progression_str.split('/')]
        else:
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

            duration_match = re.search(r'\((\d+(?:\.\d+)?)\)', chord_part)
            if duration_match:
                chord_duration = float(duration_match.group(1))
                chord_symbol = re.sub(
                    r'\(\d+(?:\.\d+)?\)', '', chord_part).strip()
            else:
                chord_duration = beats_per_measure
                chord_symbol = chord_part

            print(
                f"[progression_processor] Acorde parseado: symbol={chord_symbol}, duration={chord_duration}, bar={current_bar}, beat={current_beat}")
            parsed_chords.append({
                'symbol': chord_symbol,
                'duration': chord_duration,
                'bar': current_bar,
                'beat': current_beat
            })

            current_beat += chord_duration
            if current_beat > beats_per_measure:
                current_bar += 1
                current_beat = 1.0

        print(f"[progression_processor] Progressão parseada: {parsed_chords}")
        return parsed_chords

    def _distribute_chords_in_measure(self, chord_list: List[str], beats_per_measure: float = 4.0) -> List[str]:
        """
        Distribui acordes automaticamente em um compasso.
        Se não tiverem duração específica, divide igualmente o compasso.

        Args:
            chord_list: Lista de acordes
            beats_per_measure: Número de beats por compasso (ex: 4.0 para 4/4, 3.0 para 3/4)
        """
        print(
            f"[progression_processor] Distribuindo acordes no compasso: {chord_list} para {beats_per_measure} beats")
        result = []
        for chord in chord_list:
            chord = chord.strip()
            if not chord:
                continue
            if re.search(r'\(\d+(?:\.\d+)?\)', chord):
                result.append(chord)
            else:
                num_chords = len([c for c in chord_list if c.strip()])
                auto_duration = beats_per_measure / num_chords
                print(
                    f"[progression_processor] Atribuindo duração automática: {chord}({auto_duration})")
                result.append(f"{chord}({auto_duration})")
        print(f"[progression_processor] Resultado da distribuição: {result}")
        return result

    def process_progression(self, progression_str: str,
                            time_signature: str = "4/4",
                            tempo_bpm: int = 120,
                            key_signature: str = "C") -> List[ProgressionChord]:
        """
        Processa progressão completa retornando lista de ProgressionChords
        """
        print(
            f"[progression_processor] Processando progressão: '{progression_str}'")
        parsed_chords = self.parse_progression_string(
            progression_str, time_signature)
        progression_chords = []
        for chord_info in parsed_chords:
            try:
                print(
                    f"[progression_processor] Traduzindo acorde: {chord_info['symbol']}")
                hermeto_chord = self.translator.translate_to_hermeto_chord(
                    chord_info['symbol'])
                prog_chord = ProgressionChord(
                    hermeto_chord=hermeto_chord,
                    original_symbol=chord_info['symbol'],
                    beats=chord_info['duration'],
                    bar_number=chord_info['bar'],
                    beat_position=chord_info['beat']
                )
                print(
                    f"[progression_processor] ProgressionChord criado: {prog_chord}")
                progression_chords.append(prog_chord)
            except Exception as e:
                print(
                    f"[progression_processor] Erro ao processar acorde '{chord_info['symbol']}': {e}")
                continue
        print(
            f"[progression_processor] Progressão processada: {progression_chords}")
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
        print(
            f"[progression_processor] Gerando MusicXML para progressão: '{progression_str}'")
        progression_chords = self.process_progression(
            progression_str, time_signature, tempo_bpm, key_signature)
        if not progression_chords:
            print(
                "[progression_processor] Nenhum acorde válido encontrado na progressão!")
            raise ValueError("Nenhum acorde válido encontrado na progressão")
        score = stream.Score()
        score.append(metadata.Metadata())
        score.metadata.title = title
        score.metadata.composer = 'Sistema Hermético - Hermeto Pascoal'
        tempo_indication = tempo.TempoIndication(
            quarterLength=1, bpm=tempo_bpm)
        score.append(tempo_indication)
        score.append(key.Key(key_signature))
        score.append(meter.TimeSignature(time_signature))
        right_hand_part = stream.Part()
        right_hand_part.partName = "Mão Direita (Clave de Sol)"
        right_hand_part.append(meter.TimeSignature(time_signature))
        left_hand_part = stream.Part()
        left_hand_part.partName = "Mão Esquerda (Clave de Fá)"
        left_hand_part.append(meter.TimeSignature(time_signature))
        for prog_chord in progression_chords:
            chord_duration = duration.Duration(quarterLength=prog_chord.beats)
            print(
                f"[progression_processor] Adicionando acorde à partitura: {prog_chord.original_symbol} (beats={prog_chord.beats}, bar={prog_chord.bar_number}, beat={prog_chord.beat_position})")
            if show_chord_symbols:
                chord_text = expressions.TextExpression(
                    prog_chord.original_symbol)
                chord_text.placement = 'above'
                chord_text.quarterLength = 0
                right_hand_part.append(chord_text)
            if prog_chord.hermeto_chord.right_hand_notes:
                right_notes = []
                for note_obj in prog_chord.hermeto_chord.right_hand_notes:
                    print(
                        f"[progression_processor] Mão direita: {note_obj.name}{note_obj.octave}")
                    music21_note = note.Note(
                        pitch=f"{note_obj.name}{note_obj.octave}", quarterLength=prog_chord.beats)
                    right_notes.append(music21_note)
                if len(right_notes) == 1:
                    right_element = right_notes[0]
                    right_hand_part.append(right_element)
                else:
                    right_element = chord.Chord(
                        right_notes, quarterLength=prog_chord.beats)
                    right_hand_part.append(right_element)
            else:
                print(
                    f"[progression_processor] Mão direita: pausa ({prog_chord.beats} beats)")
                rest = note.Rest(quarterLength=prog_chord.beats)
                right_hand_part.append(rest)
            if prog_chord.hermeto_chord.left_hand_notes:
                left_notes = []
                for note_obj in prog_chord.hermeto_chord.left_hand_notes:
                    print(
                        f"[progression_processor] Mão esquerda: {note_obj.name}{note_obj.octave}")
                    music21_note = note.Note(
                        pitch=f"{note_obj.name}{note_obj.octave}", quarterLength=prog_chord.beats)
                    left_notes.append(music21_note)
                if len(left_notes) == 1:
                    left_hand_part.append(left_notes[0])
                else:
                    left_chord = chord.Chord(
                        left_notes, quarterLength=prog_chord.beats)
                    left_hand_part.append(left_chord)
            else:
                print(
                    f"[progression_processor] Mão esquerda: pausa ({prog_chord.beats} beats)")
                rest = note.Rest(quarterLength=prog_chord.beats)
                left_hand_part.append(rest)
        score.append(right_hand_part)
        score.append(left_hand_part)
        print(f"[progression_processor] MusicXML gerado com sucesso!")
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
        print(
            f"[progression_processor] Exportando progressão para MusicXML: '{progression_str}' em '{filename}'")
        score = self.generate_musicxml_progression(
            progression_str, show_chord_symbols=show_chord_symbols, **kwargs)
        score.write('musicxml', fp=filename)
        print(f"[progression_processor] Arquivo MusicXML salvo: {filename}")
        return filename

    def export_progression_midi(self, progression_str: str,
                                filename: str = "progressao_hermetica.mid",
                                show_chord_symbols: bool = False,
                                **kwargs) -> str:
        """
        Exporta progressão para arquivo MIDI

        Note: MIDI não suporta texto, então show_chord_symbols é ignorado
        """
        print(
            f"[progression_processor] Exportando progressão para MIDI: '{progression_str}' em '{filename}'")
        score = self.generate_musicxml_progression(
            progression_str, show_chord_symbols=False, **kwargs)
        score.write('midi', fp=filename)
        print(f"[progression_processor] Arquivo MIDI salvo: {filename}")
        return filename

    def analyze_progression(self, progression_str: str) -> Dict:
        """
        Analisa progressão harmônica retornando estatísticas
        """
        print(
            f"[progression_processor] Analisando progressão: '{progression_str}'")
        progression_chords = self.process_progression(progression_str)
        if not progression_chords:
            print("[progression_processor] Nenhum acorde encontrado para análise!")
            return {}
        chord_types = {}
        total_duration = 0
        chord_symbols = []
        for prog_chord in progression_chords:
            chord_type = prog_chord.hermeto_chord.chord_type
            chord_types[chord_type] = chord_types.get(chord_type, 0) + 1
            total_duration += prog_chord.beats
            chord_symbols.append(prog_chord.hermeto_chord.original_cipher)
            print(
                f"[progression_processor] Analisando acorde: {prog_chord.original_symbol} tipo={chord_type} beats={prog_chord.beats}")
        num_chords = len(progression_chords)
        avg_duration = total_duration / num_chords if num_chords > 0 else 0
        analysis = {
            'total_acordes': num_chords,
            'duracao_total_beats': total_duration,
            'duracao_media_por_acorde': avg_duration,
            'tipos_acordes': chord_types,
            'sequencia_acordes': chord_symbols,
            'complexidade_media': self._calculate_complexity(progression_chords)
        }
        print(f"[progression_processor] Resultado da análise: {analysis}")
        return analysis

    def _calculate_complexity(self, progression_chords: List[ProgressionChord]) -> float:
        """
        Calcula complexidade média da progressão
        """
        print(f"[progression_processor] Calculando complexidade média da progressão...")
        if not progression_chords:
            print("[progression_processor] Nenhum acorde para calcular complexidade.")
            return 0.0
        total_complexity = 0
        for prog_chord in progression_chords:
            chord_type = prog_chord.hermeto_chord.chord_type
            complexity = 1.0
            if chord_type == 'dominante':
                complexity += 1.0
            elif chord_type == 'meio-diminuto':
                complexity += 1.5
            elif chord_type == 'sobreposto':
                complexity += 2.0
            total_notes = (len(prog_chord.hermeto_chord.left_hand_notes) +
                           len(prog_chord.hermeto_chord.right_hand_notes))
            complexity += total_notes * 0.2
            print(
                f"[progression_processor] Complexidade do acorde {prog_chord.original_symbol}: {complexity}")
            total_complexity += complexity
        media = total_complexity / len(progression_chords)
        print(f"[progression_processor] Complexidade média: {media}")
        return media


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
