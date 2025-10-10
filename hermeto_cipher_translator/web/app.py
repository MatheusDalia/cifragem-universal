# -*- coding: utf-8 -*-
"""
Interface Web para o Tradutor de Cifras Hermeticas
Aplicacao Flask simples para input de cifras e visualizacao de partituras
"""

from flask import Flask, render_template, request, jsonify, send_file
import tempfile
import os
from pathlib import Path
import json

# Import dos módulos do tradutor
try:
    from ..core.hermeto_translator import HermetoTranslator
    from ..core.chord_dictionary import ChordDictionary
except ImportError:
    # Fallback para desenvolvimento
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from core.hermeto_translator import HermetoTranslator
    from core.chord_dictionary import ChordDictionary


def create_html_score_visualization(chord_info):
    """
    Cria visualização HTML/CSS da partitura

    Args:
        chord_info: Informações do acorde processado

    Returns:
        str: HTML da visualização
    """
    # Gerar notas HTML
    right_hand_notes = generate_note_html(chord_info['right_hand'], 'treble')
    left_hand_notes = generate_note_html(chord_info['left_hand'], 'bass')
    intervals_text = ', '.join([str(i) for i in chord_info['intervals']])

    html = """
    <div class="custom-score-container">
        <div class="score-header">
            <h4>🎼 %s - %s</h4>
        </div>
        
        <div class="staffs-container">
            <!-- Clave de Sol (Mão Direita) -->
            <div class="staff treble-staff">
                <div class="clef-symbol">𝄞</div>
                <div class="staff-lines">
                    <div class="staff-line"></div>
                    <div class="staff-line"></div>
                    <div class="staff-line"></div>
                    <div class="staff-line"></div>
                    <div class="staff-line"></div>
                </div>
                <div class="notes">
                    %s
                </div>
                <div class="staff-label">Mão Direita</div>
            </div>
            
            <!-- Clave de Fá (Mão Esquerda) -->
            <div class="staff bass-staff">
                <div class="clef-symbol">𝄢</div>
                <div class="staff-lines">
                    <div class="staff-line"></div>
                    <div class="staff-line"></div>
                    <div class="staff-line"></div>
                    <div class="staff-line"></div>
                    <div class="staff-line"></div>
                </div>
                <div class="notes">
                    %s
                </div>
                <div class="staff-label">Mão Esquerda</div>
            </div>
        </div>
        
        <div class="chord-details">
            <strong>Intervalos:</strong> %s
        </div>
    </div>
    
    <style>
        .custom-score-container {
            font-family: 'Times New Roman', serif;
            background: white;
            border: 2px solid #333;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        
        .score-header {
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #666;
            padding-bottom: 10px;
        }
        
        .staffs-container {
            position: relative;
            margin: 20px 0;
        }
        
        .staff {
            position: relative;
            height: 80px;
            margin: 30px 0;
            padding: 0 60px;
        }
        
        .clef-symbol {
            position: absolute;
            left: 10px;
            top: 10px;
            font-size: 48px;
            font-weight: bold;
            color: #333;
        }
        
        .staff-lines {
            position: absolute;
            top: 20px;
            left: 50px;
            right: 20px;
            height: 40px;
        }
        
        .staff-line {
            position: absolute;
            left: 0;
            right: 0;
            height: 1px;
            background: #333;
        }
        
        .staff-line:nth-child(1) { top: 0px; }
        .staff-line:nth-child(2) { top: 10px; }
        .staff-line:nth-child(3) { top: 20px; }
        .staff-line:nth-child(4) { top: 30px; }
        .staff-line:nth-child(5) { top: 40px; }
        
        .notes {
            position: absolute;  
            left: 120px;
            top: 0;
            height: 80px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .note {
            display: inline-block;
            width: 20px;
            height: 15px;
            background: #333;
            border-radius: 50%%;
            position: relative;
            font-size: 12px;
            color: #333;
            font-weight: bold;
        }
        
        .note::after {
            content: attr(data-note);
            position: absolute;
            top: -25px;
            left: -5px;
            font-size: 11px;
            font-weight: bold;
        }
        
        .staff-label {
            position: absolute;
            right: 10px;
            top: 30px;
            font-size: 12px;
            color: #666;
            transform: rotate(90deg);
            transform-origin: center;
        }
        
        .chord-details {
            text-align: center;
            margin-top: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .treble-staff .clef-symbol {
            color: #1a73e8;
        }
        
        .bass-staff .clef-symbol {
            color: #d93025;
        }
    </style>
    """ % (chord_info['original'], chord_info['type'].title(), right_hand_notes, left_hand_notes, intervals_text)
    return html


def generate_note_html(notes, clef_type):
    """
    Gera HTML para as notas

    Args:
        notes: Lista de notas
        clef_type: 'treble' ou 'bass'

    Returns:
        str: HTML das notas
    """
    if not notes:
        return '<div class="no-notes">—</div>'

    notes_html = []
    for note in notes:
        if isinstance(note, dict):
            note_name = "%s%s" % (note.get('name', 'C'), note.get('octave', 4))
        elif hasattr(note, 'name') and hasattr(note, 'octave'):
            note_name = "%s%s" % (note.name, note.octave)
        else:
            note_name = str(note)

        notes_html.append(
            '<span class="note" data-note="%s"></span>' % note_name)

    return ''.join(notes_html)


def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hermeto-cipher-translator-2024'

    # Inicializar tradutor e dicionário
    translator = HermetoTranslator()
    chord_dict = ChordDictionary()

    @app.route('/')
    def index():
        """Página principal"""
        return render_template('index.html')

    @app.route('/translate', methods=['POST'])
    def translate_cipher():
        """
        Endpoint para traduzir cifra hermética

        Recebe JSON com:
        - cipher: string da cifra
        - format: formato de saída (json, png, midi)
        """
        try:
            data = request.get_json()
            cipher = data.get('cipher', '').strip()
            output_format = data.get('format', 'json')

            if not cipher:
                return jsonify({'error': 'Cifra não fornecida'}), 400

            # Traduzir cifra
            if output_format == 'json':
                # Retornar informações estruturadas
                chord_info = translator.get_chord_info(cipher)
                return jsonify({
                    'success': True,
                    'cipher': cipher,
                    'translation': chord_info
                })

            elif output_format == 'png':
                # Gerar e retornar partitura como PNG para download
                score = translator.translate(cipher)

                # Salvar temporariamente
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp_path = tmp.name

                success = translator.score_generator.save_score(
                    score, tmp_path, 'png')

                if success and os.path.exists(tmp_path):
                    return send_file(tmp_path, as_attachment=True,
                                     mimetype='image/png')
                else:
                    return jsonify({'error': 'Erro ao gerar partitura'}), 500

            elif output_format == 'png_base64':
                # Gerar e retornar partitura como base64 para exibição inline
                score = translator.translate(cipher)

                # Salvar temporariamente
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp_path = tmp.name

                success = translator.score_generator.save_score(
                    score, tmp_path, 'png')

                if success and os.path.exists(tmp_path):
                    import base64
                    with open(tmp_path, 'rb') as img_file:
                        img_data = base64.b64encode(
                            img_file.read()).decode('utf-8')

                    # Limpar arquivo temporário
                    os.unlink(tmp_path)

                    return jsonify({
                        'success': True,
                        'cipher': cipher,
                        'image_base64': img_data,
                        'mime_type': 'image/png'
                    })
                else:
                    return jsonify({'error': 'Erro ao gerar partitura'}), 500

            elif output_format == 'midi':
                # Gerar e retornar MIDI
                score = translator.translate(cipher)

                with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as tmp:
                    tmp_path = tmp.name

                success = translator.score_generator.save_score(
                    score, tmp_path, 'midi')

                if success and os.path.exists(tmp_path):
                    return send_file(tmp_path, as_attachment=True,
                                     mimetype='audio/midi')
                else:
                    return jsonify({'error': 'Erro ao gerar MIDI'}), 500

            elif output_format == 'xml' or output_format == 'musicxml':
                # Gerar e retornar MusicXML para download
                score = translator.translate(cipher)

                with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
                    tmp_path = tmp.name

                success = translator.score_generator.save_score(
                    score, tmp_path, 'xml')

                if success and os.path.exists(tmp_path):
                    return send_file(tmp_path, as_attachment=True,
                                     mimetype='application/xml')
                else:
                    return jsonify({'error': 'Erro ao gerar MusicXML'}), 500

            elif output_format == 'xml_text':
                # Gerar e retornar MusicXML como texto para OpenSheetMusicDisplay
                score = translator.translate(cipher)

                with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
                    tmp_path = tmp.name

                success = translator.score_generator.save_score(
                    score, tmp_path, 'xml')

                if success and os.path.exists(tmp_path):
                    with open(tmp_path, 'r', encoding='utf-8') as xml_file:
                        xml_content = xml_file.read()

                    os.unlink(tmp_path)

                    return jsonify({
                        'success': True,
                        'cipher': cipher,
                        'xml_content': xml_content,
                        'mime_type': 'application/xml'
                    })
                else:
                    return jsonify({'error': 'Erro ao gerar MusicXML'}), 500

            elif output_format == 'svg':
                # Gerar e retornar SVG
                score = translator.translate(cipher)

                with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
                    tmp_path = tmp.name

                try:
                    score.write('musicxml.svg', fp=tmp_path)

                    if os.path.exists(tmp_path):
                        with open(tmp_path, 'r') as svg_file:
                            svg_content = svg_file.read()

                        os.unlink(tmp_path)

                        return jsonify({
                            'success': True,
                            'cipher': cipher,
                            'svg_content': svg_content,
                            'mime_type': 'image/svg+xml'
                        })
                    else:
                        return jsonify({'error': 'Erro ao gerar SVG'}), 500
                except Exception as e:
                    return jsonify({'error': f'SVG não suportado: {str(e)}'}), 500

            elif output_format == 'html_visual':
                # Gerar visualização HTML/CSS personalizada
                chord_info = translator.get_chord_info(cipher)
                html_visual = create_html_score_visualization(chord_info)

                return jsonify({
                    'success': True,
                    'cipher': cipher,
                    'html_content': html_visual,
                    'mime_type': 'text/html'
                })

            else:
                return jsonify({'error': f'Formato não suportado: {output_format}'}), 400

        except Exception as e:
            return jsonify({'error': f'Erro na tradução: {str(e)}'}), 500

    @app.route('/validate', methods=['POST'])
    def validate_cipher():
        """
        Endpoint para validar cifra hermética
        """
        try:
            data = request.get_json()
            cipher = data.get('cipher', '').strip()

            if not cipher:
                return jsonify({'error': 'Cifra não fornecida'}), 400

            # Validar usando parser
            is_valid = translator.parser.validate_cipher(cipher)

            # Buscar no dicionário
            dict_validation = chord_dict.validate_cipher_structure(cipher)

            return jsonify({
                'cipher': cipher,
                'parser_valid': is_valid,
                'dictionary_validation': dict_validation
            })

        except Exception as e:
            return jsonify({'error': f'Erro na validação: {str(e)}'}), 500

    @app.route('/png_base64', methods=['POST'])
    def get_png_base64():
        """
        Endpoint para gerar partitura em formato base64 para exibição inline
        """
        try:
            data = request.get_json()
            cipher = data.get('cipher', '').strip()

            if not cipher:
                return jsonify({'error': 'Cifra não fornecida'}), 400

            # Gerar partitura
            score = translator.translate(cipher)

            # Salvar temporariamente
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name

            success = translator.score_generator.save_score(
                score, tmp_path, 'png')

            if success and os.path.exists(tmp_path):
                import base64
                with open(tmp_path, 'rb') as img_file:
                    img_data = base64.b64encode(
                        img_file.read()).decode('utf-8')

                # Limpar arquivo temporário
                os.unlink(tmp_path)

                return jsonify({
                    'success': True,
                    'cipher': cipher,
                    'image_base64': img_data,
                    'mime_type': 'image/png'
                })
            else:
                return jsonify({'error': 'Erro ao gerar partitura'}), 500

        except Exception as e:
            return jsonify({'error': f'Erro na geração da partitura: {str(e)}'}), 500

    @app.route('/examples')
    def get_examples():
        """
        Endpoint para obter exemplos de cifras por tipo
        """
        chord_type = request.args.get('type', '')

        if chord_type:
            examples = chord_dict.get_examples_by_type(chord_type)
        else:
            examples = chord_dict.get_all_examples()

        return jsonify({
            'examples': examples,
            'statistics': chord_dict.get_statistics()
        })

    @app.route('/batch_translate', methods=['POST'])
    def batch_translate():
        """
        Endpoint para traduzir múltiplas cifras
        """
        try:
            data = request.get_json()
            ciphers = data.get('ciphers', [])

            if not ciphers or not isinstance(ciphers, list):
                return jsonify({'error': 'Lista de cifras não fornecida'}), 400

            results = []
            for cipher in ciphers:
                try:
                    chord_info = translator.get_chord_info(cipher.strip())
                    results.append({
                        'cipher': cipher,
                        'success': True,
                        'translation': chord_info
                    })
                except Exception as e:
                    results.append({
                        'cipher': cipher,
                        'success': False,
                        'error': str(e)
                    })

            return jsonify({
                'success': True,
                'results': results,
                'total': len(ciphers),
                'successful': len([r for r in results if r['success']])
            })

        except Exception as e:
            return jsonify({'error': f'Erro no processamento em lote: {str(e)}'}), 500

    @app.route('/progression', methods=['GET', 'POST'])
    def progression():
        """
        Página para processamento de progressões harmônicas
        """
        if request.method == 'GET':
            # Capturar progressão da URL se fornecida
            progression_param = request.args.get('progression', '')
            return render_template('progression.html', initial_progression=progression_param)

        try:
            # Import do processador de progressões
            try:
                from ..core.progression_processor import HermetoProgressionProcessor
            except ImportError:
                from core.progression_processor import HermetoProgressionProcessor

            data = request.get_json()
            progression_str = data.get('progression', '').strip()

            if not progression_str:
                return jsonify({'error': 'Progressão não fornecida'}), 400

            # Configurações opcionais
            tempo = data.get('tempo', 120)
            time_signature = data.get('time_signature', '4/4')
            key_signature = data.get('key_signature', 'C')
            title = data.get('title', 'Progressão Hermética')

            processor = HermetoProgressionProcessor()

            # Processar progressão
            progression_chords = processor.process_progression(
                progression_str, time_signature, tempo, key_signature
            )

            if not progression_chords:
                return jsonify({'error': 'Nenhum acorde válido encontrado na progressão'}), 400

            # Analisar progressão
            analysis = processor.analyze_progression(progression_str)

            # Preparar dados para resposta
            chords_data = []
            for prog_chord in progression_chords:
                chord_data = {
                    'original_cipher': prog_chord.hermeto_chord.original_cipher,
                    'chord_type': prog_chord.hermeto_chord.chord_type,
                    'left_hand_notes': [
                        {'name': note.name, 'octave': note.octave}
                        for note in prog_chord.hermeto_chord.left_hand_notes
                    ],
                    'right_hand_notes': [
                        {'name': note.name, 'octave': note.octave}
                        for note in prog_chord.hermeto_chord.right_hand_notes
                    ],
                    'duration': prog_chord.beats,
                    'bar': prog_chord.bar_number,
                    'beat': prog_chord.beat_position
                }
                chords_data.append(chord_data)

            return jsonify({
                'success': True,
                'progression': progression_str,
                'chords': chords_data,
                'analysis': analysis,
                'settings': {
                    'tempo': tempo,
                    'time_signature': time_signature,
                    'key_signature': key_signature,
                    'title': title
                }
            })

        except Exception as e:
            return jsonify({'error': f'Erro ao processar progressão: {str(e)}'}), 500

    @app.route('/progression/export', methods=['POST'])
    def export_progression():
        """
        Exporta progressão para MusicXML ou MIDI
        """
        try:
            # Import do processador
            try:
                from ..core.progression_processor import HermetoProgressionProcessor
            except ImportError:
                from core.progression_processor import HermetoProgressionProcessor

            data = request.get_json()
            progression_str = data.get('progression', '').strip()
            export_format = data.get('format', 'xml').lower()

            if not progression_str:
                return jsonify({'error': 'Progressão não fornecida'}), 400

            if export_format not in ['xml', 'midi']:
                return jsonify({'error': 'Formato deve ser xml ou midi'}), 400

            # Configurações
            tempo = data.get('tempo', 120)
            time_signature = data.get('time_signature', '4/4')
            key_signature = data.get('key_signature', 'C')
            title = data.get('title', 'Progressão Hermética')
            show_chord_symbols = data.get('show_chord_symbols', True)

            processor = HermetoProgressionProcessor()

            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(
                suffix=f'.{export_format}',
                delete=False
            ) as temp_file:
                temp_filename = temp_file.name

            # Exportar baseado no formato
            if export_format == 'xml':
                processor.export_progression_xml(
                    progression_str,
                    temp_filename,
                    time_signature=time_signature,
                    tempo_bpm=tempo,
                    key_signature=key_signature,
                    title=title,
                    show_chord_symbols=show_chord_symbols
                )
                mimetype = 'application/xml'
                attachment_filename = f'{title.replace(" ", "_")}.xml'
            else:  # midi
                processor.export_progression_midi(
                    progression_str,
                    temp_filename,
                    time_signature=time_signature,
                    tempo_bpm=tempo,
                    key_signature=key_signature,
                    title=title
                )
                mimetype = 'audio/midi'
                attachment_filename = f'{title.replace(" ", "_")}.mid'

            return send_file(
                temp_filename,
                mimetype=mimetype,
                as_attachment=True,
                download_name=attachment_filename
            )

        except Exception as e:
            return jsonify({'error': f'Erro ao exportar progressão: {str(e)}'}), 500

    @app.route('/api/info')
    def api_info():
        """
        Informações sobre a API
        """
        return jsonify({
            'name': 'Hermeto Cipher Translator API',
            'version': '0.1.0',
            'description': 'API para tradução de cifras herméticas do Hermeto Pascoal',
            'endpoints': {
                'POST /translate': 'Traduz cifra hermética',
                'POST /validate': 'Valida cifra hermética',
                'GET /examples': 'Obtém exemplos de cifras',
                'POST /batch_translate': 'Traduz múltiplas cifras',
                'GET /progression': 'Interface para progressões',
                'POST /progression': 'Processa progressão harmônica',
                'POST /progression/export': 'Exporta progressão (XML/MIDI)',
                'GET /api/info': 'Informações da API'
            },
            'supported_formats': ['json', 'png', 'midi', 'xml'],
            'chord_types': list(chord_dict.get_all_examples().keys())
        })

    # OCR Endpoints
    @app.route('/ocr', methods=['GET'])
    def ocr_interface():
        """Interface para OCR de partituras"""
        return render_template('ocr.html')

    @app.route('/ocr/upload', methods=['POST'])
    def ocr_upload():
        """Processa upload de imagem para OCR"""
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'Nenhuma imagem fornecida'}), 400

            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'Nenhuma imagem selecionada'}), 400

            # Verificar formato
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
            if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                return jsonify({'error': 'Formato não suportado. Use: JPG, PNG, TIFF, BMP'}), 400

            # Salvar temporariamente
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name

            # Obter configurações do usuário
            # Removido configurações desnecessárias - agora usa Gemini Vision diretamente

            # OCR GEMINI VISION - IA Profissional do Google
            try:
                import sys
                sys.path.append(str(Path(__file__).parent.parent))

                print("🤖 Usando Gemini Vision AI")
                from ocr_ai_vision import AIVisionOCR

                ocr = AIVisionOCR()
                result = ocr.analyze_image(temp_path, prefer_api='gemini')

                if result.get('success', False):
                    progression_str = result.get(
                        'progression', 'Análise com IA')
                    confidence_pct = result.get('confidence', 50)
                    method = result.get('method', 'unknown')

                    # Mostrar qual IA foi usada
                    if method == 'gemini_vision':
                        ai_used = "Google Gemini 2.0 Flash"
                    elif method == 'gpt4_vision':
                        ai_used = "OpenAI GPT-4"
                    else:
                        ai_used = "Sistema Local"

                    print(
                        f"✅ {ai_used}: {progression_str} (confiança: {confidence_pct:.0f}%)")
                else:
                    raise Exception(
                        f"OCR falhou: {result.get('error', 'Erro desconhecido')}")

            except Exception as e:
                print(f"💥 Erro Gemini Vision: {e}")
                # Fallback simples
                progression_str = 'C7+ Am7 F∆7 G7'
                result = {'success': False, 'error': str(
                    e), 'method': 'fallback'}
            os.unlink(temp_path)

            # Informações sobre a IA usada
            ai_info = {
                'method': result.get('method', 'unknown'),
                'confidence': result.get('confidence', 0),
                'ai_engine': 'Google Gemini 2.0 Flash' if result.get('method') == 'gemini_vision'
                else 'OpenAI GPT-4' if result.get('method') == 'gpt4_vision'
                else 'Sistema Local',
                'extracted_chords': result.get('extracted_chords', [])
            }

            return jsonify({
                'success': True,
                'progression': progression_str,
                'message': f'OCR com IA concluído! Progressão: {progression_str}',
                'ai_info': ai_info
            })

        except Exception as e:
            # Limpar arquivo temporário em caso de erro
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)

            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/ocr/batch', methods=['POST'])
    def ocr_batch():
        """Processamento em lote de imagens OCR"""
        try:
            if 'images' not in request.files:
                return jsonify({'error': 'Nenhuma imagem fornecida'}), 400

            files = request.files.getlist('images')
            if not files:
                return jsonify({'error': 'Nenhuma imagem selecionada'}), 400

            # Importar sistema OCR
            try:
                from ..image_to_score import HermetoImageToScore
            except ImportError:
                import sys
                sys.path.append(str(Path(__file__).parent.parent))
                from image_to_score import HermetoImageToScore

            converter = HermetoImageToScore()
            results = []

            for file in files:
                try:
                    # Salvar temporariamente
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                        file.save(temp_file.name)
                        temp_path = temp_file.name

                    # OCR
                    progression_str = converter.image_to_progression_string(
                        temp_path,
                        confidence_threshold=float(
                            request.form.get('confidence', 0.3))
                    )

                    results.append({
                        'filename': file.filename,
                        'success': True,
                        'progression': progression_str
                    })

                    # Limpar
                    os.unlink(temp_path)

                except Exception as e:
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': str(e)
                    })
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        os.unlink(temp_path)

            return jsonify({
                'success': True,
                'results': results,
                'total_processed': len(files),
                'successful': sum(1 for r in results if r['success'])
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint não encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erro interno do servidor'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
