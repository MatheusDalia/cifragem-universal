"""
Conversor de Intervalos Herméticos
Converte símbolos específicos do Hermeto (4, 5+, 7-, 9+, etc.) para intervalos musicais precisos
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class Interval:
    """Representa um intervalo musical com suas propriedades"""
    degree: int        # Grau do intervalo (1, 2, 3, 4, 5, 6, 7, 9, 11, 13)
    # Qualidade: J (justo), M (maior), m (menor), A (aumentado), d (diminuto)
    quality: str
    semitones: int     # Número de semitons do intervalo
    name: str          # Nome completo (ex: "3ª maior", "5ª justa")


class IntervalConverter:
    """
    Converte símbolos herméticos para intervalos musicais padrão

    Sistema de conversão baseado nas regras documentadas do Hermeto:
    - Números simples (4, 5, 7, 9): intervalos base
    - Com + (5+, 9+): intervalos aumentados  
    - Com - (7-, 9-, 13-): intervalos menores/diminutos
    - Contexto do acorde afeta interpretação
    """

    def __init__(self):
        print("[interval_converter] Inicializando IntervalConverter...")
        # Mapeamento base de intervalos herméticos
        self.base_intervals = {
            '1': Interval(1, 'J', 0, 'uníssono'),
            '2': Interval(2, 'M', 2, '2ª maior'),
            '3': Interval(3, 'M', 4, '3ª maior'),
            '4': Interval(4, 'J', 5, '4ª justa'),
            '5': Interval(5, 'J', 7, '5ª justa'),
            '6': Interval(6, 'M', 9, '6ª maior'),
            '7': Interval(7, 'm', 10, '7ª menor'),  # Dominante por padrão
            '8': Interval(8, 'J', 12, '8ª justa'),
            '9': Interval(9, 'M', 14, '9ª maior'),
            '11': Interval(11, 'J', 17, '11ª justa'),
            '13': Interval(13, 'M', 21, '13ª maior'),
        }

        # Alterações específicas
        self.alterations = {
            '+': {  # Aumentados
                '5': Interval(5, 'A', 8, '5ª aumentada'),
                '9': Interval(9, 'A', 15, '9ª aumentada'),
                '11': Interval(11, 'A', 18, '11ª aumentada'),
            },
            '-': {  # Menores/diminutos
                '3': Interval(3, 'm', 3, '3ª menor'),
                '5': Interval(5, 'd', 6, '5ª diminuta'),
                '7': Interval(7, 'm', 10, '7ª menor'),
                '9': Interval(9, 'm', 13, '9ª menor'),
                '13': Interval(13, 'm', 20, '13ª menor'),
            }
        }

        # Extensões automáticas por tipo de acorde
        self.chord_extensions = {
            'maior': {
                '7+': [7, 9, 13],  # D7+ = 1-3M-5J-7M-9M-13M
            },
            'menor': {
                'base': [1, 3, 5],  # Tríade menor base
            },
            'dominante': {
                'base': [1, 3, 5, 7],  # Tétrade dominante base
            },
            'suspenso': {
                'base': [1, 4, 5],  # Base sus4
            },
            'meio-diminuto': {
                'base': [1, 3, 5, 7, 9, 11],  # G#-5- = 1-3m-5d-7m-9M-11J
            }
        }

    def convert(self, parsed_data: Dict) -> Dict:
        print(
            f"[interval_converter] convert: Convertendo dados parseados: {parsed_data}")
        """
        Converte dados parseados em intervalos musicais

        Args:
            parsed_data: Dados do acorde parseado pelo ChordParser

        Returns:
            Dict: Intervalos organizados por mão e todos os intervalos
        """
        # Detectar se é acorde sobreposto
        if parsed_data.get('has_slash', False):
            print("[interval_converter] Detecção de acorde sobreposto (com barra)")
            # Acordes sobrepostos: processar cada parte separadamente
            right_intervals = self._get_automatic_extensions(
                parsed_data['right_hand'], 'direita'
            )
            print(
                f"[interval_converter] Intervalos mão direita: {right_intervals}")
            left_intervals = self._get_automatic_extensions(
                parsed_data['left_hand'], 'baixo'
            )
            print(
                f"[interval_converter] Intervalos mão esquerda: {left_intervals}")

            all_intervals = right_intervals + left_intervals
            print(f"[interval_converter] Todos intervalos: {all_intervals}")

            return {
                'right_hand': right_intervals,
                'left_hand': left_intervals,
                'all_intervals': all_intervals,
                'chord_type': parsed_data.get('chord_type', 'sobreposto')
            }
        else:
            # Acordes simples: processar como antes
            right_intervals = self._get_automatic_extensions(
                parsed_data['right_hand'], 'direita'
            )
            print(
                f"[interval_converter] Intervalos mão direita: {right_intervals}")

            print(f"[interval_converter] Todos intervalos: {right_intervals}")
            return {
                'right_hand': right_intervals,
                'left_hand': [],
                'all_intervals': right_intervals,
                'chord_type': parsed_data.get('chord_type', 'desconhecido')
            }

    def _convert_chord_part(self, part_data: Dict, context: str) -> List[Interval]:
        print(
            f"[interval_converter] _convert_chord_part: Convertendo parte '{part_data}' no contexto '{context}'")
        """
        Converte uma parte específica (direita ou esquerda) para intervalos

        Args:
            part_data: Dados de uma parte do acorde
            context: Contexto ('maior', 'menor', 'dominante', etc.)

        Returns:
            List[Interval]: Lista de intervalos para esta parte
        """
        if part_data['type'] == 'empty':
            return []

        intervals = []

        # Processar intervalos explícitos primeiro
        for interval_str in part_data.get('intervals', []):
            interval = self._parse_interval_string(interval_str, context)
            if interval:
                intervals.append(interval)

        # Adicionar extensões automáticas baseadas no tipo
        auto_intervals = self._get_automatic_extensions(part_data, context)
        intervals.extend(auto_intervals)

        # Remover duplicatas mantendo ordem
        seen = set()
        unique_intervals = []
        for interval in intervals:
            key = (interval.degree, interval.quality)
            if key not in seen:
                seen.add(key)
                unique_intervals.append(interval)

        return unique_intervals

    def _parse_interval_string(self, interval_str: str, context: str) -> Interval:
        print(
            f"[interval_converter] _parse_interval_string: Convertendo string '{interval_str}' no contexto '{context}'")
        """
        Converte string de intervalo (ex: "5+", "7-", "9") para objeto Interval

        Args:
            interval_str: String do intervalo
            context: Contexto harmônico

        Returns:
            Interval: Objeto interval correspondente
        """
        # Separar número e alteração
        if interval_str[-1] in ['+', '-']:
            number = interval_str[:-1]
            alteration = interval_str[-1]
        else:
            number = interval_str
            alteration = None

        # Buscar intervalo base
        if number in self.base_intervals:
            base_interval = self.base_intervals[number]
        else:
            # Fallback para intervalos não mapeados
            return self._create_fallback_interval(number, alteration)

        # Aplicar alteração se presente
        if alteration and alteration in self.alterations:
            if number in self.alterations[alteration]:
                return self.alterations[alteration][number]

        # Ajustar baseado no contexto
        return self._adjust_for_context(base_interval, context)

    def _adjust_for_context(self, interval: Interval, context: str) -> Interval:
        print(
            f"[interval_converter] _adjust_for_context: Ajustando intervalo '{interval}' para contexto '{context}'")
        """
        Ajusta intervalo baseado no contexto harmônico

        Args:
            interval: Intervalo base
            context: Contexto ('maior', 'menor', etc.)

        Returns:
            Interval: Intervalo ajustado
        """
        # Em acordes maiores expandidos, 7 vira 7M
        if context == 'maior' and interval.degree == 7:
            return Interval(7, 'M', 11, '7ª maior')

        # Em acordes menores, 3 vira 3m automaticamente
        if context == 'menor' and interval.degree == 3:
            return Interval(3, 'm', 3, '3ª menor')

        return interval

    def _get_automatic_extensions(self, part_data: Dict, context: str) -> List[Interval]:
        print(
            f"[interval_converter] _get_automatic_extensions: Gerando extensões automáticas para parte '{part_data}' no contexto '{context}'")
        """
        Retorna extensões automáticas baseadas no tipo de acorde

        Args:
            part_data: Dados da parte do acorde
            context: Contexto harmônico

        Returns:
            List[Interval]: Extensões automáticas
        """
        extensions = []
        chord_type = part_data.get('type', context)
        original_part = part_data.get('original_part', '')

        # TRATAMENTO ESPECIAL PARA BAIXO (mão esquerda em acordes sobrepostos)
        if context == 'baixo':
            # Para baixo: sempre incluir fundamental
            extensions = [self.base_intervals['1']]

            # Adicionar apenas os intervalos explícitos (não gerar acorde completo)
            intervals_list = part_data.get('intervals', [])
            for interval_str in intervals_list:
                interval = self._parse_interval_string(
                    interval_str, chord_type)
                if interval and interval.degree != 1:  # Não duplicar fundamental
                    extensions.append(interval)

            return extensions

        # TRATAMENTO NORMAL PARA MÃO DIREITA (acordes completos)

        # Acordes suspensos com intervalos específicos (Ex: C458)
        elif chord_type == 'suspenso':
            intervals_list = part_data.get('intervals', [])

            # Para acordes como C458: C F G C (oitava)
            if '4' in intervals_list and '5' in intervals_list and '8' in intervals_list:
                extensions = [
                    self.base_intervals['1'],           # C (fundamental)
                    self.base_intervals['4'],           # F (4ª justa)
                    self.base_intervals['5'],           # G (5ª justa)
                    self.base_intervals['8']            # C (oitava)
                ]
            # Para acordes como F6: F + D (6ª)
            elif '6' in intervals_list:
                extensions = [
                    self.base_intervals['1'],           # Fundamental
                    self.base_intervals['6']            # 6ª maior
                ]
            else:
                # Base sus4 + intervalos específicos
                extensions = [self.base_intervals['1']]  # Sempre fundamental
                for interval_str in intervals_list:
                    interval = self._parse_interval_string(
                        interval_str, chord_type)
                    if interval and interval.degree != 1:
                        extensions.append(interval)

        # Detectar acordes menores com 7ª (Ex: Em7, Fm7, etc.)
        elif 'm7' in original_part and chord_type == 'tetrade':
            # Acorde menor com 7ª: 1-3m-5J-7m
            extensions = [
                self.base_intervals['1'],                    # 1 (fundamental)
                Interval(3, 'm', 3, '3ª menor'),            # 3m (terça menor)
                # 5J (quinta justa)
                self.base_intervals['5'],
                # 7m (sétima menor)
                self.base_intervals['7']
            ]

        # Acordes de 7ª dominante (Ex: Ab7, G7, C7, etc.)
        elif chord_type == 'tetrade' and 'm7' not in original_part:
            # Acorde dominante: 1-3M-5J-7m
            extensions = [
                self.base_intervals['1'],                    # 1 (fundamental)
                self.base_intervals['3'],                    # 3M (terça maior)
                # 5J (quinta justa)
                self.base_intervals['5'],
                # 7m (sétima menor)
                self.base_intervals['7']
            ]

        # Acordes maiores: verificar se é expansão (7+) ou tríade simples
        elif chord_type == 'maior' or chord_type == 'maior_com_7+':
            intervals_list = part_data.get('intervals', [])

            if '7+' in intervals_list:
                # Caso especial: C7+ (apenas 7+ sem outras tensões) = acorde maior expandido completo
                if intervals_list == ['7+']:
                    # Acorde maior expandido completo: 1-3M-5J-7M-9M-13M
                    extensions = [
                        # 1 (fundamental)
                        self.base_intervals['1'],
                        # 3M (terça maior)
                        self.base_intervals['3'],
                        # 5J (quinta justa)
                        self.base_intervals['5'],
                        # 7M (sétima maior)
                        Interval(7, 'M', 11, '7ª maior'),
                        # 9M (nona maior)
                        self.base_intervals['9'],
                        # 13M (décima terceira maior)
                        self.base_intervals['13']
                    ]
                else:
                    # D7+9+11+ (com outras tensões específicas): apenas as especificadas
                    extensions = [
                        # 1 (fundamental)
                        self.base_intervals['1'],
                        # 3M (terça maior)
                        self.base_intervals['3'],
                        # 5J (quinta justa)
                        self.base_intervals['5'],
                        # 7M (sétima maior)
                        Interval(7, 'M', 11, '7ª maior')
                    ]

                    # Adicionar apenas as outras tensões específicas (9+, 11+, etc.)
                    for interval_str in intervals_list:
                        if interval_str != '7+':  # Já adicionamos a 7M
                            interval = self._parse_interval_string(
                                interval_str, chord_type)
                            if interval:
                                # Verificar se já existe
                                exists = any(ext.degree == interval.degree and ext.quality == interval.quality
                                             for ext in extensions)
                                if not exists:
                                    extensions.append(interval)

            elif not intervals_list:
                # Tríade maior simples (apenas letra)
                extensions = [
                    self.base_intervals['1'],
                    self.base_intervals['3'],
                    self.base_intervals['5']
                ]
            else:
                # Acorde maior com outras extensões
                extensions = [
                    self.base_intervals['1'],
                    self.base_intervals['3'],
                    self.base_intervals['5']
                ]

                # Adicionar extensões específicas
                for interval_str in intervals_list:
                    interval = self._parse_interval_string(
                        interval_str, chord_type)
                    if interval:
                        exists = any(ext.degree == interval.degree and ext.quality == interval.quality
                                     for ext in extensions)
                        if not exists:
                            extensions.append(interval)

        # Acordes menores: tratar caso específico -479
        elif chord_type == 'menor':
            intervals_list = part_data.get('intervals', [])

            # Caso específico C-479: estrutura completa definida
            if set(intervals_list) == {'4', '7', '9'}:
                # C-479 = 1-4J-7m (esquerda) + 9M-3m-5J (direita)
                # Retornar TODOS os intervalos necessários
                extensions = [
                    self.base_intervals['1'],           # 1 (C)
                    Interval(3, 'm', 3, '3ª menor'),    # 3m (Eb)
                    self.base_intervals['4'],           # 4J (F)
                    self.base_intervals['5'],           # 5J (G)
                    self.base_intervals['7'],           # 7m (Bb)
                    self.base_intervals['9']            # 9M (D)
                ]
            elif not intervals_list:
                # Tríade menor simples
                extensions = [
                    self.base_intervals['1'],
                    Interval(3, 'm', 3, '3ª menor'),
                    self.base_intervals['5']
                ]

        # Acordes meio-diminutos (ex: G#-5-)
        elif chord_type == 'meio-diminuto':
            # Estrutura fixa: 1 – 3m – 5d – 7m – 9M – 11J
            extensions = [
                self.base_intervals['1'],                    # 1 (uníssono)
                Interval(3, 'm', 3, '3ª menor'),            # 3m
                Interval(5, 'd', 6, '5ª diminuta'),         # 5d
                self.base_intervals['7'],                    # 7m
                self.base_intervals['9'],                    # 9M
                Interval(11, 'J', 17, '11ª justa')          # 11J
            ]

        # Acordes dominantes com alterações (ex: F#79+13-, A5+7)
        elif chord_type == 'dominante':
            # Para baixo em acordes sobrepostos: apenas fundamental + intervalos explícitos
            if context == 'baixo':
                extensions = [self.base_intervals['1']]  # Sempre fundamental

                # Adicionar apenas os intervalos explícitos
                intervals_list = part_data.get('intervals', [])
                for interval_str in intervals_list:
                    interval = self._parse_interval_string(
                        interval_str, 'dominante')
                    if interval and interval.degree != 1:  # Não duplicar fundamental
                        extensions.append(interval)
            else:
                # Para mão direita: base dominante + alterações
                extensions = [
                    self.base_intervals['1'],
                    self.base_intervals['3'],
                    self.base_intervals['5'],
                    self.base_intervals['7']  # 7m
                ]

                # Adicionar intervalos parseados (preservar 9-, 11+, 13, etc.)
                intervals_list = part_data.get('intervals', [])
                for interval_str in intervals_list:
                    interval = self._parse_interval_string(
                        interval_str, 'dominante')
                    if interval:
                        # Verificar se já existe (por degree, não por objeto)
                        exists = any(ext.degree == interval.degree and ext.quality == interval.quality
                                     for ext in extensions)
                        if not exists:
                            extensions.append(interval)

        return extensions

    def _create_fallback_interval(self, number: str, alteration: str) -> Interval:
        print(
            f"[interval_converter] _create_fallback_interval: Criando fallback para número '{number}' com alteração '{alteration}'")
        """
        Cria intervalo para números não mapeados

        Args:
            number: Número do intervalo
            alteration: Alteração (+/-)

        Returns:
            Interval: Intervalo aproximado
        """
        try:
            degree = int(number)
            # Cálculo aproximado de semitons
            base_semitones = {
                1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 10,
                8: 12, 9: 14, 10: 16, 11: 17, 12: 19, 13: 21
            }

            semitones = base_semitones.get(degree % 8, degree % 8 * 2)
            if degree > 8:
                semitones += 12

            if alteration == '+':
                semitones += 1
                quality = 'A'
            elif alteration == '-':
                semitones -= 1
                quality = 'd'
            else:
                quality = 'M' if degree in [2, 3, 6, 7] else 'J'

            return Interval(degree, quality, semitones, f'{degree}ª {quality}')

        except ValueError:
            # Fallback extremo
            return Interval(1, 'J', 0, 'uníssono')

    def get_interval_name(self, interval: Interval) -> str:
        print(
            f"[interval_converter] get_interval_name: Nome para intervalo '{interval}'")
        """
        Retorna nome legível do intervalo

        Args:
            interval: Objeto Interval

        Returns:
            str: Nome do intervalo
        """
        return interval.name

    def intervals_to_semitones(self, intervals: List[Interval]) -> List[int]:
        print(
            f"[interval_converter] intervals_to_semitones: Convertendo intervalos para semitons: {intervals}")
        """
        Converte lista de intervalos para lista de semitons

        Args:
            intervals: Lista de intervalos

        Returns:
            List[int]: Lista de semitons correspondentes
        """
        return [interval.semitones for interval in intervals]
