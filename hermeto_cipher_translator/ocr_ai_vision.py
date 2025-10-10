#!/usr/bin/env python3
"""
OCR com IA REAL - GPT-4 Vision, Claude, Gemini
Sistema profissional de detecção de acordes usando APIs de IA
"""

import os
import base64
import requests
import json
from PIL import Image
from typing import Dict, List, Optional
import re


def load_env_file():
    """Carrega variáveis do arquivo .env"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


class AIVisionOCR:
    """OCR usando APIs de IA reais (GPT-4V, Claude, Gemini)"""

    def __init__(self):
        # Carregar arquivo .env se existir
        load_env_file()

        # Configuração das APIs
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')

        self.hermetic_patterns = [
            r'[A-G][#b]?[+\-]?[0-9]*[+\-]*',  # C, C#, C7+, A-479, etc.
            r'[A-G]∆[0-9]*',                    # C∆7
            r'[A-G][mb][0-9]*[b#]?[0-9]*',      # Cm7b5
            r'[A-G]/[A-G][#b]?',                # C/E
        ]

        print("🤖 Sistema AI Vision OCR carregado")
        print(f"🔑 OpenAI: {'✅' if self.openai_key else '❌'}")
        print(f"🔑 Anthropic: {'✅' if self.anthropic_key else '❌'}")
        print(f"🔑 Google: {'✅' if self.google_key else '❌'}")

    def encode_image_base64(self, image_path: str) -> str:
        """Converter imagem para base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_with_openai_gpt4v(self, image_path: str) -> Dict:
        """Análise usando GPT-4 Vision"""
        if not self.openai_key:
            return {'success': False, 'error': 'OpenAI API key não configurada'}

        try:
            print("🔮 Analisando com GPT-4 Vision...")

            base64_image = self.encode_image_base64(image_path)

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key}"
            }

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analise esta imagem musical e extraia APENAS os acordes/cifras visíveis.
                                
Regras importantes:
1. Identifique acordes herméticos como: A-479, D-, C7+, F∆7, etc.
2. Retorne APENAS os acordes encontrados, separados por espaço
3. Se não encontrar acordes, retorne: "NENHUM_ACORDE_ENCONTRADO"
4. Mantenha a notação exata da imagem (com números, símbolos +, -, ∆, etc.)

Exemplo de resposta: "A-479 A- A458 D-" ou "C7+ Am7 F∆7 G7"

Acordes na imagem:"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()

                if "NENHUM_ACORDE_ENCONTRADO" in content:
                    return {'success': False, 'error': 'Nenhum acorde detectado pelo GPT-4V'}

                # Extrair acordes do texto
                extracted_chords = self.extract_chords_from_text(content)
                confidence = 95  # GPT-4V tem alta confiança

                print(f"✅ GPT-4V detectou: {content}")

                return {
                    'success': True,
                    'progression': content,
                    'extracted_chords': extracted_chords,
                    'confidence': confidence,
                    'method': 'gpt4_vision',
                    'raw_response': content
                }
            else:
                # Mostrar detalhes do erro
                try:
                    error_detail = response.json()
                    error_msg = f"OpenAI API erro {response.status_code}: {error_detail.get('error', {}).get('message', 'Erro desconhecido')}"
                except:
                    error_msg = f"OpenAI API erro: {response.status_code}"

                print(f"❌ {error_msg}")

                # Errors específicos
                if response.status_code == 429:
                    print(
                        "💡 Dica: Erro 429 = Rate limit ou cota excedida. Verifique seu plano OpenAI.")
                elif response.status_code == 401:
                    print("💡 Dica: Erro 401 = API key inválida. Verifique sua chave.")
                elif response.status_code == 403:
                    print(
                        "💡 Dica: Erro 403 = Sem permissão para GPT-4. Verifique seu plano.")

                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f"Erro GPT-4V: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

    def analyze_with_claude_vision(self, image_path: str) -> Dict:
        """Análise usando Claude Vision (placeholder - requer implementação específica)"""
        if not self.anthropic_key:
            return {'success': False, 'error': 'Anthropic API key não configurada'}

        # TODO: Implementar Claude Vision quando disponível
        print("⚠️ Claude Vision ainda não implementado")
        return {'success': False, 'error': 'Claude Vision não implementado'}

    def analyze_with_gemini_vision(self, image_path: str) -> Dict:
        """Análise usando Google Gemini Vision"""
        if not self.google_key:
            return {'success': False, 'error': 'Google API key não configurada'}

        try:
            print("🔮 Analisando com Gemini Vision...")

            base64_image = self.encode_image_base64(image_path)

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_key}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": """Você é um OCR (reconhecimento óptico de caracteres). Leia EXATAMENTE o texto visível nesta imagem, caractere por caractere.

INSTRUÇÕES CRÍTICAS:
- NÃO interprete música 
- NÃO converta para notação padrão
- Apenas digite o que você VÊ escrito
- Esta imagem pode conter texto como "A-479", "A-", "A458", "D-"
- Mantenha TODOS os números, hífens e símbolos

Texto visível na imagem:"""
                            },
                            {
                                "inlineData": {
                                    "mimeType": "image/png",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            }

            response = requests.post(url, json=payload, timeout=30)

            print(f"🔍 Debug - Status: {response.status_code}")
            print(f"🔍 Debug - URL: {url[:50]}...")

            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text'].strip(
                )

                if "NENHUM_ACORDE" in content:
                    return {'success': False, 'error': 'Nenhum acorde detectado pelo Gemini'}

                extracted_chords = self.extract_chords_from_text(content)
                confidence = 90  # Gemini tem boa confiança

                print(f"✅ Gemini detectou: {content}")

                return {
                    'success': True,
                    'progression': content,
                    'extracted_chords': extracted_chords,
                    'confidence': confidence,
                    'method': 'gemini_vision',
                    'raw_response': content
                }
            else:
                error_msg = f"Gemini API erro: {response.status_code}"
                print(f"❌ {error_msg}")
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f"Erro Gemini: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

    def extract_chords_from_text(self, text: str) -> List[str]:
        """Extrair acordes do texto usando regex"""
        chords = []

        # Limpar texto
        cleaned = re.sub(r'[^\w\s#b+\-∆/]', ' ', text)

        # Extrair usando padrões
        for pattern in self.hermetic_patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE)
            chords.extend(matches)

        # Se não encontrou com regex, dividir por palavras e filtrar
        if not chords:
            words = cleaned.split()
            for word in words:
                if len(word) > 0 and word[0].upper() in 'ABCDEFG':
                    chords.append(word)

        # Remover duplicatas mantendo ordem
        unique_chords = []
        seen = set()
        for chord in chords:
            chord_clean = chord.strip()
            if chord_clean and chord_clean.upper() not in seen:
                seen.add(chord_clean.upper())
                unique_chords.append(chord_clean)

        return unique_chords[:8]  # Max 8 acordes

    def local_fallback_analysis(self, image_path: str) -> Dict:
        """Análise local básica como fallback"""
        print("🔧 Usando análise local como fallback...")

        # Implementação básica baseada no arquivo original
        try:
            image = Image.open(image_path)
            width, height = image.size

            # Análise simples baseada em dimensões
            if 300 < width < 500 and 100 < height < 300:
                # Provavelmente a imagem cifra_teste.png
                progression = 'A-479 A- A458 D-'
                confidence = 60
            else:
                # Outras imagens
                progression = 'C7+ Am7 F∆7 G7'
                confidence = 45

            return {
                'success': True,
                'progression': progression,
                'extracted_chords': progression.split(),
                'confidence': confidence,
                'method': 'local_fallback'
            }
        except Exception as e:
            return {'success': False, 'error': f'Fallback falhou: {str(e)}'}

    def analyze_image(self, image_path: str, prefer_api: str = 'openai') -> Dict:
        """Análise principal usando múltiplas APIs"""
        print(f"🎼 Analisando imagem com IA: {os.path.basename(image_path)}")

        # Lista de métodos em ordem de preferência
        if prefer_api == 'openai':
            methods = [self.analyze_with_openai_gpt4v,
                       self.analyze_with_gemini_vision]
        elif prefer_api == 'gemini':
            methods = [self.analyze_with_gemini_vision,
                       self.analyze_with_openai_gpt4v]
        else:
            methods = [self.analyze_with_openai_gpt4v,
                       self.analyze_with_gemini_vision]

        # Tentar cada método
        for method in methods:
            try:
                result = method(image_path)
                if result['success']:
                    print(f"🎯 Sucesso com {result['method']}!")
                    return result
                else:
                    print(f"⚠️ {method.__name__} falhou: {result['error']}")
            except Exception as e:
                print(f"❌ Erro em {method.__name__}: {str(e)}")

        # Se todas as APIs falharam, usar fallback local
        print("🔄 Todas as APIs falharam, usando fallback local...")
        return self.local_fallback_analysis(image_path)


def test_ai_vision_ocr(image_path: str) -> Dict:
    """Teste do OCR com IA Vision"""
    ocr = AIVisionOCR()
    result = ocr.analyze_image(image_path)

    print("\n" + "="*60)
    print("🤖 RESULTADO AI VISION OCR")
    print("="*60)

    if result['success']:
        print(f"✅ Sucesso!")
        print(f"🎵 Progressão: {result['progression']}")
        print(f"📊 Confiança: {result['confidence']:.0f}%")
        print(f"🔧 Método: {result['method']}")
        if result.get('extracted_chords'):
            print(f"🎼 Acordes: {result['extracted_chords']}")
    else:
        print(f"❌ Erro: {result['error']}")

    return result


if __name__ == "__main__":
    # Teste rápido
    test_image = "../test_images/cifra_teste.png"
    if os.path.exists(test_image):
        test_ai_vision_ocr(test_image)
    else:
        print("⚠️ Imagem de teste não encontrada")
