import cv2
import pytesseract
import re
import subprocess
import os
from typing import List, Dict

# 1. Pré-processamento da imagem


def preprocess_image(image_path: str) -> str:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # Binarização adaptativa
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 35, 15)
    # Remoção de ruído
    img = cv2.medianBlur(img, 3)
    # Salvar imagem pré-processada
    processed_path = image_path.replace('.jpg', 'partitura_hermeto.jpg')
    cv2.imwrite(processed_path, img)
    return processed_path

# 2. Extração de texto/cifras manuscritas


def extract_chords_from_image(image_path: str) -> List[str]:
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(
        image_path, config=custom_config, lang='por')
    # Regex para cifras (ex: A-479, E9+, D7+, etc)
    chord_pattern = r'[A-G][#b]?[-+]?\d*(?:[a-zA-Z0-9+\-]*)'
    chords = re.findall(chord_pattern, text)
    # Filtrar acordes válidos
    chords = [c for c in chords if len(c) > 1]
    return chords

# 3. Extração de notas com Audiveris (MusicXML)


def run_audiveris(image_path: str, audiveris_path: str = 'Audiveris') -> str:
    # Audiveris precisa estar instalado e no PATH
    output_dir = 'audiveris_output'
    os.makedirs(output_dir, exist_ok=True)
    cmd = [audiveris_path, '-batch', image_path,
           '-export', 'xml', '-output', output_dir]
    subprocess.run(cmd, check=True)
    # Procurar MusicXML gerado
    for fname in os.listdir(output_dir):
        if fname.endswith('.xml'):
            return os.path.join(output_dir, fname)
    return ''

# 4. Traduzir acordes usando dicionário customizado


def translate_chords(chords: List[str], chord_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
    translated = {}
    for chord in chords:
        notes = chord_dict.get(chord, [])
        translated[chord] = notes
    return translated

# 5. Gerar MusicXML customizado (estrutura inicial)


def generate_custom_musicxml(notes: List[str], chords: Dict[str, List[str]], base_xml_path: str = None) -> str:
    # Aqui você pode usar o base_xml_path do Audiveris e inserir os acordes traduzidos
    # Exemplo: apenas retorna caminho do XML original
    return base_xml_path or ''


# Exemplo de uso
if __name__ == '__main__':
    image_path = 'partitura_hermeto.jpg'  # Caminho da imagem
    processed_path = preprocess_image(image_path)
    chords = extract_chords_from_image(processed_path)
    print('Cifras extraídas:', chords)

    # Audiveris (ajuste caminho se necessário)
    # xml_path = run_audiveris(processed_path)
    # print('MusicXML gerado:', xml_path)

    # Dicionário de acordes (exemplo)
    chord_dict = {
        'A-479': ['A', 'C', 'E', 'G', 'B'],
        'E9+': ['E', 'G#', 'B', 'D', 'F#'],
        # ...
    }
    translated = translate_chords(chords, chord_dict)
    print('Acordes traduzidos:', translated)

    # MusicXML customizado (estrutura inicial)
    # custom_xml = generate_custom_musicxml([], translated, xml_path)
    # print('MusicXML final:', custom_xml)
