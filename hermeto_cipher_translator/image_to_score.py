#!/usr/bin/env python3
"""
Integração OCR + Sistema de Tradução Hermética
Pipeline completo: Imagem → OCR → Tradução → Partitura
"""

import os
from typing import List, Dict
from core.progression_processor import HermetoProgressionProcessor
from core.hermeto_translator import HermetoTranslator


class HermetoImageToScore:
    """
    Sistema completo de conversão: Imagem de partitura → Partitura digital
    """

    def __init__(self):
        # Detectar automaticamente melhor OCR disponível
        self.ocr = self._get_best_ocr()
        self.translator = HermetoTranslator()
        self.progression_processor = HermetoProgressionProcessor()

    def _get_best_ocr(self):
        """Detecta e retorna a melhor opção de OCR disponível (priorizando velocidade)"""
        try:
            # PRIMEIRA OPÇÃO: OCR Simples (sem dependências)
            from ocr_simple import SimpleHermetoOCR
            ocr = SimpleHermetoOCR()
            print("🚀 Usando OCR Simples (sem dependências, instantâneo)")
            return ocr
        except Exception as e:
            try:
                # SEGUNDA OPÇÃO: OCR rápido para demonstrações
                from ocr_fast import HermetoOCRQuick
                ocr = HermetoOCRQuick(mode='demo')
                print("⚡ Usando OCR Rápido (modo demo)")
                return ocr
            except Exception as e2:
                try:
                    # TERCEIRA OPÇÃO: OCR alternativo se disponível
                    from ocr_alternative import HermetoOCRAlternative
                    ocr = HermetoOCRAlternative()
                    print("✅ Usando EasyOCR (mais lento)")
                    return ocr
                except Exception as e3:
                    try:
                        # QUARTA OPÇÃO: Tesseract se disponível
                        from ocr_hermeto import HermetoOCR
                        ocr = HermetoOCR()
                        print("✅ Usando Tesseract OCR")
                        return ocr
                    except Exception as e4:
                        raise ImportError(
                            f"Nenhum sistema OCR disponível. Erro: {e}")

    def image_to_progression_string(self, image_path: str,
                                    confidence_threshold: float = 0.3) -> str:
        """
        Converte imagem em string de progressão

        Args:
            image_path: Caminho da imagem
            confidence_threshold: Confiança mínima para incluir cifra

        Returns:
            str: String de progressão ("Am7 | C7+ | D-479")
        """
        print(f"🔍 Extraindo cifras de: {os.path.basename(image_path)}")

        # 1. OCR para extrair cifras
        cipher_regions = self.ocr.process_score_image(image_path, debug=True)

        # 2. Filtrar por confiança
        valid_ciphers = [
            region.processed_text
            for region in cipher_regions
            if region.confidence >= confidence_threshold
        ]

        if not valid_ciphers:
            raise ValueError(
                "Nenhuma cifra detectada com confiança suficiente")

        # 3. Formar string de progressão
        progression_str = " | ".join(valid_ciphers)

        print(f"✅ Progressão extraída: {progression_str}")
        return progression_str

    def image_to_musicxml(self, image_path: str,
                          output_path: str = None,
                          **musicxml_params) -> str:
        """
        Pipeline completo: Imagem → MusicXML

        Args:
            image_path: Caminho da imagem
            output_path: Caminho de saída (opcional)
            **musicxml_params: Parâmetros para MusicXML (tempo, tonalidade, etc.)

        Returns:
            str: Caminho do arquivo MusicXML gerado
        """
        print("🔄 Pipeline completo: Imagem → MusicXML")
        print("=" * 40)

        # 1. OCR
        progression_str = self.image_to_progression_string(image_path)

        # 2. Definir arquivo de saída
        if not output_path:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = f"{base_name}_hermeto.xml"

        # 3. Parâmetros padrão
        default_params = {
            'tempo_bpm': 120,
            'time_signature': '4/4',
            'key_signature': 'C',
            'title': f'Partitura Hermética - {os.path.basename(image_path)}',
            'show_chord_symbols': True
        }
        default_params.update(musicxml_params)

        # 4. Gerar MusicXML
        print("🎼 Gerando partitura...")
        xml_file = self.progression_processor.export_progression_xml(
            progression_str,
            output_path,
            **default_params
        )

        print(f"✅ MusicXML gerado: {xml_file}")
        return xml_file

    def validate_extracted_ciphers(self, cipher_regions: List) -> Dict:
        """
        Valida cifras extraídas testando tradução

        Args:
            cipher_regions: Regiões de cifras detectadas (lista de objetos com texto e confiança)

        Returns:
            Dict: Estatísticas de validação
        """
        stats = {
            'total_detected': len(cipher_regions),
            'valid_translations': 0,
            'invalid_translations': 0,
            'validation_details': []
        }

        for region in cipher_regions:
            try:
                # Tentar traduzir a cifra
                hermeto_chord = self.translator.translate_to_hermeto_chord(
                    region.processed_text
                )

                stats['valid_translations'] += 1
                stats['validation_details'].append({
                    'cipher': region.processed_text,
                    'confidence': region.confidence,
                    'status': 'valid',
                    'notes_count': len(hermeto_chord.right_hand_notes) + len(hermeto_chord.left_hand_notes)
                })

            except Exception as e:
                stats['invalid_translations'] += 1
                stats['validation_details'].append({
                    'cipher': region.processed_text,
                    'confidence': region.confidence,
                    'status': 'invalid',
                    'error': str(e)
                })

        # Calcular taxa de sucesso
        if stats['total_detected'] > 0:
            stats['success_rate'] = stats['valid_translations'] / \
                stats['total_detected']
        else:
            stats['success_rate'] = 0.0

        return stats

    def batch_process_images(self, directory_path: str, output_dir: str = None) -> Dict:
        """
        Processa lote de imagens

        Args:
            directory_path: Diretório com imagens
            output_dir: Diretório de saída (opcional)

        Returns:
            Dict: Resultados do processamento
        """
        if not output_dir:
            output_dir = os.path.join(directory_path, "hermeto_scores")

        os.makedirs(output_dir, exist_ok=True)

        results = {
            'processed_files': [],
            'successful_conversions': 0,
            'failed_conversions': 0,
            'total_ciphers_detected': 0,
            'details': {}
        }

        # Formatos suportados
        supported_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']

        for filename in os.listdir(directory_path):
            if not any(filename.lower().endswith(fmt) for fmt in supported_formats):
                continue

            image_path = os.path.join(directory_path, filename)
            results['processed_files'].append(filename)

            try:
                print(f"\n📸 Processando: {filename}")

                # OCR
                cipher_regions = self.ocr.process_score_image(
                    image_path, debug=True)
                results['total_ciphers_detected'] += len(cipher_regions)

                # Validação
                validation_stats = self.validate_extracted_ciphers(
                    cipher_regions)

                # Se há cifras válidas, gerar MusicXML
                if validation_stats['valid_translations'] > 0:
                    output_file = os.path.join(
                        output_dir,
                        f"{os.path.splitext(filename)[0]}_hermeto.xml"
                    )

                    xml_file = self.image_to_musicxml(image_path, output_file)
                    results['successful_conversions'] += 1

                    results['details'][filename] = {
                        'status': 'success',
                        'xml_file': xml_file,
                        'validation': validation_stats
                    }
                else:
                    results['failed_conversions'] += 1
                    results['details'][filename] = {
                        'status': 'failed',
                        'reason': 'no_valid_ciphers',
                        'validation': validation_stats
                    }

            except Exception as e:
                results['failed_conversions'] += 1
                results['details'][filename] = {
                    'status': 'error',
                    'error': str(e)
                }
                print(f"❌ Erro processando {filename}: {e}")

        return results

    def generate_batch_report(self, results: Dict, output_path: str = "ocr_batch_report.txt"):
        """Gera relatório detalhado do processamento em lote"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("🎼 RELATÓRIO DE PROCESSAMENTO OCR - CIFRAS HERMÉTICAS\n")
            f.write("=" * 60 + "\n\n")

            # Resumo geral
            f.write("📊 RESUMO GERAL\n")
            f.write("-" * 30 + "\n")
            f.write(
                f"Arquivos processados: {len(results['processed_files'])}\n")
            f.write(
                f"Conversões bem-sucedidas: {results['successful_conversions']}\n")
            f.write(f"Conversões falhadas: {results['failed_conversions']}\n")
            f.write(
                f"Total de cifras detectadas: {results['total_ciphers_detected']}\n")

            success_rate = (results['successful_conversions'] /
                            len(results['processed_files']) * 100
                            if results['processed_files'] else 0)
            f.write(f"Taxa de sucesso: {success_rate:.1f}%\n\n")

            # Detalhes por arquivo
            f.write("📋 DETALHES POR ARQUIVO\n")
            f.write("-" * 30 + "\n")

            for filename, details in results['details'].items():
                f.write(f"\n🎵 {filename}\n")
                f.write(f"   Status: {details['status']}\n")

                if 'validation' in details:
                    val = details['validation']
                    f.write(f"   Cifras detectadas: {val['total_detected']}\n")
                    f.write(
                        f"   Traduções válidas: {val['valid_translations']}\n")
                    f.write(
                        f"   Taxa de validação: {val['success_rate']:.1f}%\n")

                if 'xml_file' in details:
                    f.write(f"   Arquivo gerado: {details['xml_file']}\n")

                if 'error' in details:
                    f.write(f"   Erro: {details['error']}\n")

        print(f"📄 Relatório salvo: {output_path}")


def demo_complete_pipeline():
    """Demonstração do pipeline completo"""
    print("🎼 PIPELINE COMPLETO: IMAGEM → PARTITURA HERMÉTICA")
    print("=" * 55)

    converter = HermetoImageToScore()

    print("🛠️ Sistema pronto para uso!")
    print("\n📋 Funcionalidades disponíveis:")
    print("1. converter.image_to_progression_string('partitura.jpg')")
    print("2. converter.image_to_musicxml('partitura.jpg')")
    print("3. converter.batch_process_images('pasta_com_imagens/')")

    print("\n🎯 Para usar com suas imagens:")
    print("- Coloque imagens de partituras do Hermeto em uma pasta")
    print("- Execute: converter.batch_process_images('caminho/pasta')")
    print("- Sistema gerará MusicXML para cada imagem processada")

    return converter


if __name__ == "__main__":
    demo_complete_pipeline()
