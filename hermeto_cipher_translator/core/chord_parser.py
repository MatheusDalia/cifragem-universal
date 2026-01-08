"""
Parser de Cifras Herméticas
Analisa e interpreta strings de cifras no sistema do Hermeto Pascoal
"""

import re
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ParsedChordData:
    """Estrutura de dados para acorde hermético parseado"""
    original: str
    chord_type: str  # maior, menor, dominante, suspenso, meio-diminuto, sobreposto
    root: str  # Nota fundamental
    right_hand: Dict  # Dados para mão direita (clave Sol)
    left_hand: Dict   # Dados para mão esquerda (clave Fá)
    has_slash: bool   # Se é acorde sobreposto (tem barra /)


class ChordParser:
    """
    Parser principal para cifras herméticas do Hermeto Pascoal

    Exemplos suportados:
    - D7+: Acorde maior expandido
    - C-479: Acorde menor com intervalos
    - F#79+13-: Dominante com alterações
    - F 4 7 9: Suspenso
    - G#-5-: Meio-diminuto
    - A/F6: Sobreposto (A na direita, F6 na esquerda)
    - Em7/Ab6: Tetrade/sexta sobreposta
    """

    def __init__(self):
        print("[chord_parser] Inicializando ChordParser...")
        # Regex patterns para diferentes tipos de acordes
        self.patterns = {
            'note': r'[A-G][#b]?',
            'slash': r'/',
            'numbers': r'\d+',
            'alterations': r'[+\-]',
            'minor': r'-',
            'major_seventh': r'\+',
            'tetrad_suffix': r'(m7|7|maj7|M7|\+)',
        }

    def parse(self, cipher: str) -> Dict:
        print(f"[chord_parser] parse: Recebido cifra '{cipher}' para parsing.")
        """
        Parse principal de uma cifra hermética

        Args:
            cipher: String da cifra (ex: "C458/A5+7")

        Returns:
            Dict: Dados estruturados do acorde parseado
        """
        cipher = cipher.strip()
        print(f"[chord_parser] Limpo cifra: '{cipher}'")
        # Verificar se é acorde sobreposto (tem barra /)
        if '/' in cipher:
            print(f"[chord_parser] Detecção de acorde sobreposto (com barra)")
            return self._parse_slash_chord(cipher)
        else:
            print(f"[chord_parser] Detecção de acorde simples (sem barra)")
            return self._parse_simple_chord(cipher)

    def _parse_slash_chord(self, cipher: str) -> Dict:
        print(
            f"[chord_parser] _parse_slash_chord: Parsing cifra sobreposta '{cipher}'")
        """
        Parse de acordes sobrepostos (formato: direita/esquerda)

        Args:
            cipher: Cifra com barra (ex: "A/F6", "Em7/Ab6")

        Returns:
            Dict: Dados do acorde sobreposto
        """
        parts = cipher.split('/')
        if len(parts) != 2:
            print(f"[chord_parser] Erro: cifra sobreposta inválida!")
            raise ValueError(f"Cifra sobreposta inválida: {cipher}")

        right_part = parts[0].strip()  # Mão direita (antes da barra)
        left_part = parts[1].strip()   # Mão esquerda (depois da barra)
        print(
            f"[chord_parser] Mão direita: '{right_part}', Mão esquerda: '{left_part}'")

        # Parse da parte direita
        right_data = self._parse_chord_part(right_part)
        print(f"[chord_parser] Dados da mão direita: {right_data}")

        # Parse da parte esquerda
        left_data = self._parse_chord_part(left_part)
        print(f"[chord_parser] Dados da mão esquerda: {left_data}")

        result = {
            'original': cipher,
            'chord_type': 'sobreposto',
            'root': right_data['root'],
            'right_hand': right_data,
            'left_hand': left_data,
            'has_slash': True
        }
        print(f"[chord_parser] Resultado do parsing sobreposto: {result}")
        return result

    def _parse_simple_chord(self, cipher: str) -> Dict:
        print(
            f"[chord_parser] _parse_simple_chord: Parsing cifra simples '{cipher}'")
        """
        Parse de acordes simples (sem barra)

        Args:
            cipher: Cifra simples (ex: "D7+", "C-479", "F 4 7 9")

        Returns:
            Dict: Dados do acorde simples
        """
        chord_data = self._parse_chord_part(cipher)
        print(f"[chord_parser] Dados do acorde simples: {chord_data}")
        result = {
            'original': cipher,
            'chord_type': chord_data['type'],
            'root': chord_data['root'],
            'right_hand': chord_data,
            'left_hand': {'type': 'empty', 'root': None, 'intervals': []},
            'has_slash': False
        }
        print(f"[chord_parser] Resultado do parsing simples: {result}")
        return result

    def _parse_chord_part(self, part: str) -> Dict:
        print(f"[chord_parser] _parse_chord_part: Parsing parte '{part}'")
        """
        Parse de uma parte individual do acorde

        Args:
            part: Parte da cifra (ex: "C458", "Em7", "F6")

        Returns:
            Dict: Dados da parte parseada
        """
        # Extrair nota fundamental
        root_match = re.match(r'^([A-G][#b]?)', part)
        if not root_match:
            print(f"[chord_parser] Erro: nota fundamental não encontrada!")
            raise ValueError(f"Nota fundamental não encontrada em: {part}")

        root = root_match.group(1)
        remaining = part[len(root):]
        print(
            f"[chord_parser] Nota fundamental extraída: '{root}', restante: '{remaining}'")

        # Determinar tipo de acorde baseado no conteúdo
        chord_type = self._determine_chord_type(remaining)
        print(f"[chord_parser] Tipo de acorde determinado: '{chord_type}'")

        # Extrair intervalos e alterações
        intervals = self._extract_intervals(remaining)
        print(f"[chord_parser] Intervalos extraídos: {intervals}")

        result = {
            'type': chord_type,
            'root': root,
            'intervals': intervals,
            'original_part': part
        }
        print(f"[chord_parser] Resultado do parsing da parte: {result}")
        return result

    def _determine_chord_type(self, remaining: str) -> str:
        print(
            f"[chord_parser] _determine_chord_type: Determinando tipo para '{remaining}'")
        """
        Determina o tipo de acorde baseado nos símbolos

        Args:
            remaining: Parte da cifra após a nota fundamental

        Returns:
            str: Tipo do acorde
        """
        if not remaining:
            print(f"[chord_parser] Tipo: maior (apenas nota)")
            return 'maior'  # Apenas a letra = tríade maior

        # Tétrades conhecidas
        if re.search(r'^(m7|7|maj7|M7)$', remaining):
            print(f"[chord_parser] Tipo: tetrade")
            return 'tetrade'

        # Acorde maior expandido hermético (ex: 7+, 7+9+11+) - deve vir ANTES de dominante
        if '7+' in remaining:
            print(f"[chord_parser] Tipo: maior (hermético 7+)")
            return 'maior'

        # Padrão específico 679 ou -79 (acordes maiores/menores com extensões)
        if re.match(r'^-?679$', remaining):
            if remaining.startswith('-'):
                print(f"[chord_parser] Tipo: menor (padrão -679)")
                return 'menor'
            else:
                print(f"[chord_parser] Tipo: maior (padrão 679)")
                return 'maior'

        if re.match(r'^-79$', remaining):
            print(f"[chord_parser] Tipo: menor (padrão -79)")
            return 'menor'

        # Padrão específico 79 (dominante com 7 e 9)
        if re.match(r'^79$', remaining):
            print(f"[chord_parser] Tipo: dominante (padrão 79)")
            return 'dominante'

        # Acorde menor (começa com -)
        if remaining.startswith('-'):
            # Meio-diminuto se tem -5-
            if '-5-' in remaining:
                print(f"[chord_parser] Tipo: meio-diminuto")
                return 'meio-diminuto'
            else:
                print(f"[chord_parser] Tipo: menor")
                return 'menor'

        # Dominante com alterações (números + alterações, mas SEM 7+)
        if re.search(r'\d+[+\-]', remaining) and '7+' not in remaining:
            print(f"[chord_parser] Tipo: dominante (alterações)")
            return 'dominante'

        # Outros acordes maiores expandidos
        if '+' in remaining and ('7' in remaining or '9' in remaining):
            print(f"[chord_parser] Tipo: maior (expansão)")
            return 'maior'

        # Suspenso (apenas números sem sinais de +/-)
        if re.search(r'^\s*\d+(\s+\d+)*\s*$', remaining.replace(' ', '')):
            print(f"[chord_parser] Tipo: suspenso")
            return 'suspenso'

        # Intervalos explícitos (números com ou sem alterações)
        if re.search(r'\d', remaining):
            print(f"[chord_parser] Tipo: intervalos")
            return 'intervalos'

        print(f"[chord_parser] Tipo: maior (default)")
        return 'maior'  # Default

    def _extract_intervals(self, intervals_str: str) -> List[str]:
        print(
            f"[chord_parser] _extract_intervals: Extraindo intervalos de '{intervals_str}'")
        """
        Extrai intervalos de uma string como '79+13-' -> ['7', '9+', '13-']

        Args:
            intervals_str: String com intervalos concatenados

        Returns:
            List[str]: Lista de intervalos separados
        """
        if not intervals_str:
            return []

        intervals = []
        i = 0

        while i < len(intervals_str):
            # Começar a capturar um número
            num_str = ""

            # Capturar dígitos do número
            while i < len(intervals_str) and intervals_str[i].isdigit():
                num_str += intervals_str[i]
                i += 1

            if num_str:
                # Verificar se há alteração (+/-)
                if i < len(intervals_str) and intervals_str[i] in ['+', '-']:
                    alteration = intervals_str[i]
                    i += 1

                    # Intervalos conhecidos de 2 dígitos não devem ser separados
                    if num_str in ['11', '13']:
                        intervals.append(num_str + alteration)
                    else:
                        # Separar números de múltiplos dígitos (ex: "79+" -> "7", "9+")
                        if len(num_str) > 1:
                            for j, digit in enumerate(num_str):
                                if j == len(num_str) - 1:  # Último dígito recebe a alteração
                                    intervals.append(digit + alteration)
                                else:
                                    intervals.append(digit)
                        else:
                            intervals.append(num_str + alteration)
                else:
                    # Sem alteração - separar apenas se não for intervalo conhecido
                    if num_str in ['11', '13']:
                        intervals.append(num_str)
                    else:
                        # Separar números de múltiplos dígitos
                        for digit in num_str:
                            intervals.append(digit)
            else:
                # Caractere não numérico, pular
                i += 1

        return intervals

    def validate_cipher(self, cipher: str) -> bool:
        """
        Valida se uma cifra está no formato esperado

        Args:
            cipher: String da cifra a validar

        Returns:
            bool: True se válida, False caso contrário
        """
        try:
            self.parse(cipher)
            return True
        except (ValueError, IndexError, AttributeError):
            return False

    def get_chord_examples(self) -> Dict[str, List[str]]:
        """
        Retorna exemplos de cifras por tipo

        Returns:
            Dict: Exemplos organizados por tipo de acorde
        """
        return {
            'maior': ['D7+', 'C', 'F7+9+13'],
            'menor': ['C-479', 'Am', 'Fm-579'],
            'dominante': ['F#79+13-', 'G7alt', 'A79-11+13'],
            'suspenso': ['F 4 7 9', 'Csus4', 'D sus2'],
            'meio-diminuto': ['G#-5-', 'Bø7', 'C#-5-79'],
            'sobreposto': ['A/F6', 'Em7/Ab6', 'C458/A5+7'],
            'tetrade': ['Cm7', 'D7', 'Amaj7', 'GM7']
        }

    def _classify_chord_type(self, root: str, intervals: List[str]) -> str:
        """
        Classifica o tipo do acorde baseado nos intervalos presentes

        Args:
            root: Nota fundamental
            intervals: Lista de intervalos

        Returns:
            str: Tipo do acorde
        """
        # PRIMEIRO: Verificar se tem 7ª maior (7+) - indica acorde maior com extensões
        if '7+' in intervals:
            return 'maior_com_7+'

        # Verificar se tem intervalos menores (3-, ou símbolo -)
        elif any('-' in interval for interval in intervals if '3' in interval) or root.endswith('m'):
            # Casos especiais de acordes menores
            if set(intervals) == {'4', '7', '9'}:
                return 'menor'  # Caso específico C-479
            elif '5-' in intervals:
                return 'meio-diminuto'
            else:
                return 'menor'

        # Verificar se é acorde dominante (tem 7 sem +, mas não é menor)
        elif '7' in intervals and '7+' not in intervals:
            return 'dominante'

        # Verificar se tem muitas alterações (mas SEM 7+)
        elif len([i for i in intervals if '+' in i or '-' in i]) >= 2 and '7+' not in intervals:
            return 'dominante'

        # Verificar se é suspenso (tem números sem + ou -)
        elif any(i.isdigit() for i in intervals):
            return 'suspenso'

        # Default: maior
        else:
            return 'maior'
