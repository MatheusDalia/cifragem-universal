"""
Gerador de Partituras
Cria partituras visuais usando music21 a partir das notas organizadas nas claves
"""

from typing import Dict, List, Optional, Tuple
import os
from pathlib import Path

try:
    from music21 import stream, note, pitch, clef, meter, key, bar, layout, duration, chord
    from music21 import environment
    from music21.musicxml import m21ToXml
except ImportError:
    print("Warning: music21 not installed. Install with: pip install music21")
    # Fallback para desenvolvimento sem music21

    class MockMusic21:
        class stream:
            class Score:
                pass

        class note:
            class Note:
                pass

        class pitch:
            class Pitch:
                pass

        class clef:
            class TrebleClef:
                pass

            class BassClef:
                pass

    stream = MockMusic21.stream
    note = MockMusic21.note
    pitch = MockMusic21.pitch
    clef = MockMusic21.clef

from .note_generator import Note


class ScoreGenerator:
    """
    Gera partituras de piano a partir de notas organizadas por clave

    Cria scores no music21 com:
    - Clave de Sol (mão direita)
    - Clave de Fá (mão esquerda)  
    - Formatação apropriada para piano
    - Exportação para PNG, PDF, MIDI, MusicXML
    """

    def __init__(self):
        # Configurar environment do music21
        try:
            self.env = environment.Environment()
            # Tentar configurar path para MuseScore (necessário para PNG/PDF)
            self._setup_musescore()
        except:
            self.env = None

        # Configurações padrão de partitura
        if 'key' in globals():
            self.default_key = key.Key('C')
            self.default_time = meter.TimeSignature('4/4')
            self.note_duration = duration.Duration(
                'whole')  # Semibreve para acordes
        else:
            self.default_key = None
            self.default_time = None
            self.note_duration = None

    def _setup_musescore(self):
        """
        Configura MuseScore para exportação de imagens
        """
        try:
            # Caminhos comuns do MuseScore no macOS
            musescore_paths = [
                '/Applications/MuseScore 4.app/Contents/MacOS/mscore',
                '/Applications/MuseScore 3.app/Contents/MacOS/mscore',
                '/usr/local/bin/musescore',
                '/opt/homebrew/bin/musescore'
            ]

            for path in musescore_paths:
                if os.path.exists(path):
                    self.env['musescoreDirectPNGPath'] = path
                    break
        except Exception as e:
            print(f"Warning: Could not configure MuseScore: {e}")

    def create_score(self, staff_data: Dict):
        """
        Cria partitura completa a partir das notas distribuídas

        Args:
            staff_data: Dados com notas organizadas por clave

        Returns:
            Score object (music21.stream.Score se disponível, dict caso contrário)
        """
        if 'stream' not in globals():
            # Fallback sem music21: retornar dados estruturados
            return {
                'type': 'simple_score',
                'treble_clef': [note.name + str(note.octave) for note in staff_data['right_hand']],
                'bass_clef': [note.name + str(note.octave) for note in staff_data['left_hand']],
                'original_cipher': staff_data.get('original', ''),
                'metadata': {
                    'title': f"Cifra Hermética: {staff_data.get('original', 'Unknown')}",
                    'composer': 'Hermeto Pascoal (Sistema de Cifragem)'
                }
            }

        try:
            # Criar score principal
            score = stream.Score()

            # Adicionar metadados
            score.metadata = self._create_metadata(staff_data)

            # Adicionar armadura e compasso
            if self.default_key:
                score.append(self.default_key)
            if self.default_time:
                score.append(self.default_time)

            # Criar parte da mão direita (clave de Sol)
            treble_part = self._create_treble_part(staff_data['right_hand'])
            treble_part.partName = "Mão Direita"
            treble_part.partAbbreviation = "MD"
            score.append(treble_part)

            # Criar parte da mão esquerda (clave de Fá)
            bass_part = self._create_bass_part(staff_data['left_hand'])
            bass_part.partName = "Mão Esquerda"
            bass_part.partAbbreviation = "ME"
            score.append(bass_part)

            # Aplicar formatação de piano
            self._format_piano_score(score)

            return score

        except Exception as e:
            print(f"Error creating score: {e}")
            return self._create_fallback_score(staff_data)

    def _create_treble_part(self, notes: List[Note]) -> 'stream.Part':
        """
        Cria parte da clave de Sol (mão direita)

        Args:
            notes: Lista de notas para clave de Sol

        Returns:
            music21.stream.Part: Parte da clave de Sol
        """
        part = stream.Part()
        part.append(clef.TrebleClef())

        if not notes:
            # Adicionar pausa se não houver notas
            rest = note.Rest(duration=self.note_duration)
            part.append(rest)
        else:
            # Criar acorde ou notas individuais
            if len(notes) == 1:
                # Nota única
                music_note = self._note_to_music21(notes[0])
                part.append(music_note)
            else:
                # Acorde (múltiplas notas simultâneas)
                chord = self._create_chord(notes)
                part.append(chord)

        return part

    def _create_bass_part(self, notes: List[Note]) -> 'stream.Part':
        """
        Cria parte da clave de Fá (mão esquerda)

        Args:
            notes: Lista de notas para clave de Fá

        Returns:
            music21.stream.Part: Parte da clave de Fá
        """
        part = stream.Part()
        part.append(clef.BassClef())

        if not notes:
            # Adicionar pausa se não houver notas
            rest = note.Rest(duration=self.note_duration)
            part.append(rest)
        else:
            # Criar acorde ou notas individuais
            if len(notes) == 1:
                # Nota única
                music_note = self._note_to_music21(notes[0])
                part.append(music_note)
            else:
                # Acorde (múltiplas notas simultâneas)
                chord = self._create_chord(notes)
                part.append(chord)

        return part

    def _note_to_music21(self, our_note: Note) -> 'note.Note':
        """
        Converte nossa classe Note para music21.note.Note

        Args:
            our_note: Nossa classe Note

        Returns:
            music21.note.Note: Nota do music21
        """
        try:
            # Criar pitch
            pitch_obj = pitch.Pitch(f"{our_note.name}{our_note.octave}")

            # Criar nota com duração
            music_note = note.Note(pitch_obj, duration=self.note_duration)

            return music_note

        except Exception as e:
            print(f"Error converting note {our_note.name}: {e}")
            # Fallback para Dó central
            return note.Note('C4', duration=self.note_duration)

    def _create_chord(self, notes: List[Note]) -> 'note.Note':
        """
        Cria acorde music21 a partir de lista de notas

        Args:
            notes: Lista de notas

        Returns:
            music21.note.Note: Acorde (nota com múltiplos pitches)
        """
        try:
            # Converter notas para pitches
            pitches = []
            for our_note in notes:
                pitch_obj = pitch.Pitch(f"{our_note.name}{our_note.octave}")
                pitches.append(pitch_obj)

            # Criar acorde
            chord_obj = chord.Chord(pitches, duration=self.note_duration)

            return chord_obj

        except Exception as e:
            print(f"Error creating chord: {e}")
            # Fallback para primeira nota
            if notes:
                return self._note_to_music21(notes[0])
            else:
                return note.Note('C4', duration=self.note_duration)

    def _create_metadata(self, staff_data: Dict) -> 'stream.Metadata':
        """
        Cria metadados da partitura

        Args:
            staff_data: Dados da distribuição

        Returns:
            music21.stream.Metadata: Metadados
        """
        try:
            from music21 import metadata

            meta = metadata.Metadata()
            meta.title = f"Cifra Hermética: {staff_data.get('original', 'Unknown')}"
            meta.composer = 'Hermeto Pascoal (Sistema de Cifragem)'
            meta.software = 'Hermeto Cipher Translator'

            return meta

        except Exception:
            return None

    def _format_piano_score(self, score: 'stream.Score'):
        """
        Aplica formatação específica para piano

        Args:
            score: Score para formatar
        """
        try:
            # Adicionar layout de piano (duas claves)
            piano_layout = layout.StaffGroup(
                [score.parts[0], score.parts[1]], name='Piano', symbol='brace')
            score.insert(0, piano_layout)

        except Exception as e:
            print(f"Warning: Could not apply piano formatting: {e}")

    def _create_fallback_score(self, staff_data: Dict) -> 'stream.Score':
        """
        Cria score simples em caso de erro

        Args:
            staff_data: Dados da distribuição

        Returns:
            music21.stream.Score: Score básico
        """
        try:
            score = stream.Score()
            part = stream.Part()
            part.append(clef.TrebleClef())
            part.append(note.Note('C4', duration=duration.Duration('whole')))
            score.append(part)
            return score
        except:
            return None

    def save_score(self, score: 'stream.Score', filepath: str, format: str = 'png') -> bool:
        """
        Salva partitura em arquivo

        Args:
            score: Partitura para salvar
            filepath: Caminho do arquivo
            format: Formato ('png', 'pdf', 'midi', 'xml')

        Returns:
            bool: True se sucesso, False se erro
        """
        try:
            if not score:
                return False

            # Criar diretório se não existir
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == 'png':
                score.write('musicxml.png', fp=filepath)
            elif format.lower() == 'pdf':
                score.write('musicxml.pdf', fp=filepath)
            elif format.lower() == 'midi':
                score.write('midi', fp=filepath)
            elif format.lower() in ['xml', 'musicxml']:
                score.write('musicxml', fp=filepath)
            else:
                print(f"Unsupported format: {format}")
                return False

            return True

        except Exception as e:
            print(f"Error saving score: {e}")
            return False

    def show_score(self, score: 'stream.Score'):
        """
        Exibe partitura (abre no visualizador padrão)

        Args:
            score: Partitura para exibir
        """
        try:
            if score:
                score.show()
        except Exception as e:
            print(f"Error showing score: {e}")

    def score_to_midi_data(self, score: 'stream.Score') -> Optional[bytes]:
        """
        Converte partitura para dados MIDI

        Args:
            score: Partitura

        Returns:
            Optional[bytes]: Dados MIDI ou None se erro
        """
        try:
            if not score:
                return None

            # Converter para MIDI stream
            midi_stream = score.write('midi')
            return midi_stream

        except Exception as e:
            print(f"Error converting to MIDI: {e}")
            return None

    def score_to_png_data(self, score: 'stream.Score') -> Optional[bytes]:
        """
        Converte partitura para dados PNG

        Args:
            score: Partitura

        Returns:
            Optional[bytes]: Dados PNG ou None se erro
        """
        try:
            if not score:
                return None

            # Por enquanto, criar uma imagem placeholder simples
            # TODO: Resolver problema de integração com MuseScore 4

            from PIL import Image, ImageDraw, ImageFont
            import io

            # Criar imagem placeholder
            width, height = 800, 400
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)

            # Tentar usar uma fonte padrão
            try:
                # Fonte maior para o título
                font_title = ImageFont.truetype(
                    '/System/Library/Fonts/Arial.ttf', 24)
                font_text = ImageFont.truetype(
                    '/System/Library/Fonts/Arial.ttf', 16)
            except:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()

            # Desenhar título
            draw.text((50, 50), "Hermeto Cipher Translator",
                      fill='black', font=font_title)
            draw.text((50, 100), "Partitura Gerada",
                      fill='black', font=font_text)

            # Adicionar informações do acorde
            y_pos = 150
            if hasattr(score, 'parts') and score.parts:
                for i, part in enumerate(score.parts):
                    part_name = f"Parte {i+1}"
                    draw.text((50, y_pos), part_name,
                              fill='black', font=font_text)
                    y_pos += 30

                    # Tentar listar algumas notas
                    notes = []
                    for element in part.flatten():
                        if hasattr(element, 'pitch'):
                            notes.append(str(element.pitch))
                        elif hasattr(element, 'pitches'):  # Acorde
                            notes.extend([str(p) for p in element.pitches])

                    if notes:
                        notes_text = "Notas: " + \
                            ", ".join(notes[:8])  # Máximo 8 notas
                        if len(notes) > 8:
                            notes_text += "..."
                        draw.text((70, y_pos), notes_text,
                                  fill='gray', font=font_text)
                        y_pos += 25

            # Adicionar nota sobre MuseScore
            draw.text((50, height - 80), "Nota: Integração com MuseScore em desenvolvimento",
                      fill='red', font=font_text)
            draw.text((50, height - 50), "Esta é uma imagem placeholder",
                      fill='red', font=font_text)

            # Converter para bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()

        except Exception as e:
            print(f"Error converting to PNG: {e}")
            return None

    def get_score_info(self, score: 'stream.Score') -> Dict:
        """
        Retorna informações sobre a partitura

        Args:
            score: Partitura

        Returns:
            Dict: Informações da partitura
        """
        try:
            if not score:
                return {'error': 'No score provided'}

            info = {
                'parts': len(score.parts),
                'measures': len(score.parts[0].getElementsByClass('Measure')) if score.parts else 0,
                'notes_treble': len(score.parts[0].flat.notes) if len(score.parts) > 0 else 0,
                'notes_bass': len(score.parts[1].flat.notes) if len(score.parts) > 1 else 0,
                'duration': float(score.duration.quarterLength) if hasattr(score, 'duration') else 0,
                'key': str(score.analyze('key')) if hasattr(score, 'analyze') else 'Unknown'
            }

            return info

        except Exception as e:
            return {'error': f'Could not analyze score: {e}'}
