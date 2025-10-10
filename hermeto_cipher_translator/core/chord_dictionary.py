"""
Dicionário de Acordes Herméticos
Base de dados com exemplos e validações de cifras do sistema Hermeto
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


class ChordDictionary:
    """
    Dicionário de acordes herméticos com exemplos documentados

    Contém:
    - Cifras conhecidas e suas traduções
    - Exemplos de cada tipo de acorde
    - Validações de entrada
    - Padrões de distribuição específicos
    """

    def __init__(self, data_file: Optional[str] = None):
        self.data_file = data_file or self._get_default_data_file()
        self.chord_data = self._load_chord_data()

    def _get_default_data_file(self) -> str:
        """Retorna caminho padrão do arquivo de dados"""
        return str(Path(__file__).parent.parent / "data" / "hermeto_chords.json")

    def _load_chord_data(self) -> Dict:
        """Carrega dados de acordes do arquivo JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_data()
        except json.JSONDecodeError:
            print(f"Error reading {self.data_file}, using defaults")
            return self._create_default_data()

    def _create_default_data(self) -> Dict:
        """Cria dados padrão baseados na documentação do Hermeto"""
        return {
            "maior": {
                "D7+": {
                    "description": "Acorde maior expandido",
                    "structure": "1-3M-5J-7M-9M-13M",
                    "notes": ["D", "F#", "A", "C#", "E", "B"],
                    "distribution": {
                        "right_hand": ["D", "F#", "A", "C#", "E", "B"],
                        "left_hand": []
                    }
                }
            },
            "menor": {
                "C-479": {
                    "description": "Acorde menor com distribuição específica",
                    "structure": "1-4J-7m (esquerda) + 9M-3m-5J (direita)",
                    "notes": ["C", "F", "Bb", "D", "Eb", "G"],
                    "distribution": {
                        "right_hand": ["D", "Eb", "G"],
                        "left_hand": ["C", "F", "Bb"]
                    }
                }
            },
            "dominante": {
                "F#79+13-": {
                    "description": "Dominante com 9+ e 13-",
                    "structure": "1-3M-5J-7m-9A-13m",
                    "notes": ["F#", "A#", "C#", "E", "G##", "D"],
                    "distribution": {
                        "right_hand": ["F#", "A#", "C#", "E", "G##", "D"],
                        "left_hand": []
                    }
                }
            },
            "suspenso": {
                "F 4 7 9": {
                    "description": "Acorde suspenso",
                    "structure": "1-4J-5J-7m-9M",
                    "notes": ["F", "Bb", "C", "Eb", "G"],
                    "distribution": {
                        "right_hand": ["F", "Bb", "C", "Eb", "G"],
                        "left_hand": []
                    }
                }
            },
            "meio-diminuto": {
                "G#-5-": {
                    "description": "Meio-diminuto expandido",
                    "structure": "1-3m-5d-7m-9M-11J",
                    "notes": ["G#", "B", "D", "F#", "A#", "C#"],
                    "distribution": {
                        "right_hand": ["G#", "B", "D", "F#"],
                        "left_hand": ["A#", "C#"]
                    }
                }
            },
            "sobreposto": {
                "A/F6": {
                    "description": "Tríade A sobre baixo F6",
                    "structure": "A maior (direita) + F-D (esquerda)",
                    "notes": ["A", "C#", "E", "F", "D"],
                    "distribution": {
                        "right_hand": ["A", "C#", "E"],
                        "left_hand": ["F", "D"]
                    }
                },
                "Em7/Ab6": {
                    "description": "Tetrade Em7 sobre Ab6",
                    "structure": "Em7 (direita) + Ab-F (esquerda)",
                    "notes": ["E", "G", "B", "D", "Ab", "F"],
                    "distribution": {
                        "right_hand": ["E", "G", "B", "D"],
                        "left_hand": ["Ab", "F"]
                    }
                },
                "C458/A5+7": {
                    "description": "C com intervalos sobre A alterado",
                    "structure": "C-F-G-C (direita) + A-F-G (esquerda)",
                    "notes": ["C", "F", "G", "A"],
                    "distribution": {
                        "right_hand": ["C", "F", "G", "C"],
                        "left_hand": ["A", "F", "G"]
                    }
                }
            },
            "tetrade": {
                "Em7": {
                    "description": "Acorde menor com sétima",
                    "structure": "1-3m-5J-7m",
                    "notes": ["E", "G", "B", "D"],
                    "distribution": {
                        "right_hand": ["E", "G", "B", "D"],
                        "left_hand": []
                    }
                }
            },
            "intervalos": {
                "C458": {
                    "description": "Acorde com intervalos específicos",
                    "structure": "1-4J-5J-8J",
                    "notes": ["C", "F", "G", "C"],
                    "distribution": {
                        "right_hand": ["C", "F", "G", "C"],
                        "left_hand": []
                    }
                }
            }
        }

    def save_data(self):
        """Salva dados atuais no arquivo JSON"""
        try:
            Path(self.data_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.chord_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving chord data: {e}")
            return False

    def get_chord_example(self, cipher: str) -> Optional[Dict]:
        """
        Busca exemplo de uma cifra específica

        Args:
            cipher: Cifra hermética

        Returns:
            Optional[Dict]: Dados do acorde se encontrado
        """
        for chord_type, chords in self.chord_data.items():
            if cipher in chords:
                return {
                    'cipher': cipher,
                    'type': chord_type,
                    **chords[cipher]
                }
        return None

    def get_examples_by_type(self, chord_type: str) -> Dict:
        """
        Retorna todos os exemplos de um tipo de acorde

        Args:
            chord_type: Tipo do acorde

        Returns:
            Dict: Exemplos do tipo
        """
        return self.chord_data.get(chord_type, {})

    def add_chord_example(self, cipher: str, chord_type: str, data: Dict) -> bool:
        """
        Adiciona novo exemplo de acorde

        Args:
            cipher: Cifra hermética
            chord_type: Tipo do acorde
            data: Dados do acorde

        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            if chord_type not in self.chord_data:
                self.chord_data[chord_type] = {}

            self.chord_data[chord_type][cipher] = data
            return True
        except Exception:
            return False

    def validate_cipher_structure(self, cipher: str) -> Dict:
        """
        Valida estrutura de uma cifra baseada nos exemplos

        Args:
            cipher: Cifra para validar

        Returns:
            Dict: Resultado da validação
        """
        # Buscar exemplo exato
        example = self.get_chord_example(cipher)
        if example:
            return {
                'valid': True,
                'found': 'exact',
                'example': example,
                'confidence': 1.0
            }

        # Buscar padrões similares
        similar = self._find_similar_patterns(cipher)
        if similar:
            return {
                'valid': True,
                'found': 'similar',
                'similar_patterns': similar,
                'confidence': 0.7
            }

        return {
            'valid': False,
            'found': 'none',
            'confidence': 0.0,
            'message': 'Cifra não encontrada nos exemplos'
        }

    def _find_similar_patterns(self, cipher: str) -> List[Dict]:
        """
        Encontra padrões similares à cifra

        Args:
            cipher: Cifra de entrada

        Returns:
            List[Dict]: Padrões similares encontrados
        """
        similar = []

        # Extrair características da cifra
        has_slash = '/' in cipher
        has_minus = '-' in cipher
        has_plus = '+' in cipher
        has_numbers = any(c.isdigit() for c in cipher)

        # Buscar acordes com características similares
        for chord_type, chords in self.chord_data.items():
            for existing_cipher, data in chords.items():
                score = 0

                # Comparar características
                if ('/' in existing_cipher) == has_slash:
                    score += 1
                if ('-' in existing_cipher) == has_minus:
                    score += 1
                if ('+' in existing_cipher) == has_plus:
                    score += 1
                if any(c.isdigit() for c in existing_cipher) == has_numbers:
                    score += 1

                # Se tem pelo menos 2 características em comum
                if score >= 2:
                    similar.append({
                        'cipher': existing_cipher,
                        'type': chord_type,
                        'similarity_score': score / 4,
                        'data': data
                    })

        # Ordenar por similaridade
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar[:5]  # Top 5 similares

    def get_all_examples(self) -> Dict:
        """Retorna todos os exemplos organizados por tipo"""
        return self.chord_data

    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do dicionário

        Returns:
            Dict: Estatísticas dos acordes
        """
        stats = {
            'total_chords': 0,
            'by_type': {},
            'most_complex': None,
            'simplest': None
        }

        max_notes = 0
        min_notes = float('inf')

        for chord_type, chords in self.chord_data.items():
            count = len(chords)
            stats['by_type'][chord_type] = count
            stats['total_chords'] += count

            for cipher, data in chords.items():
                note_count = len(data.get('notes', []))

                if note_count > max_notes:
                    max_notes = note_count
                    stats['most_complex'] = {
                        'cipher': cipher,
                        'type': chord_type,
                        'note_count': note_count
                    }

                if note_count < min_notes:
                    min_notes = note_count
                    stats['simplest'] = {
                        'cipher': cipher,
                        'type': chord_type,
                        'note_count': note_count
                    }

        return stats
