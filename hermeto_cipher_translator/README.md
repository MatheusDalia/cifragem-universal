# Tradutor de Cifras Herméticas do Hermeto Pascoal

🎼 Ferramenta computacional para traduzir o sistema único de cifragem do Hermeto Pascoal em partituras de piano (claves de Sol e Fá).

## 🎯 Objetivo

Hermeto Pascoal desenvolveu um sistema próprio de cifragem musical que não possui documentação formal ou dicionário de acordes. Esta ferramenta automatiza a conversão dessas cifras "herméticas" para partitura tradicional de piano.

## 🏗️ Arquitetura

### Módulos Principais:

- **`chord_parser.py`** - Analisa e interpreta cifras herméticas (ex: "C458/A5+7")
- **`interval_converter.py`** - Converte símbolos (4, 5+, 7-, 9+) para intervalos musicais
- **`note_generator.py`** - Transforma intervalos em notas absolutas (C, F#, Bb)
- **`staff_distributor.py`** - Distribui notas entre claves Sol (direita) e Fá (esquerda)
- **`score_generator.py`** - Gera partituras visuais usando music21
- **`chord_dictionary.py`** - Base de dados de acordes herméticos

### Sistema de Cifras Herméticas:

1. **Acordes Maiores**: `D7+` → 1-3M-5J-7M-9M-13M
2. **Acordes Menores**: `C-479` → Distribuição específica entre mãos
3. **Dominantes**: `F#79+13-` → Alterações em 9ª, 11ª, 13ª
4. **Suspensos**: `F 4 7 9` → Estrutura 1-4J-7m-9M
5. **Meio-diminutos**: `G#-5-` → Com 9M e 11J adicionais
6. **Sobrepostos**: `A/F6` → Mão direita / Mão esquerda

## 🚀 Instalação

### Instalação Básica

```bash
cd hermeto_cipher_translator
pip install -e .
```

### 🔍 Sistema OCR (NOVO!)

Para reconhecimento automático de cifras em imagens:

**Opção 1 - Instalação Simples (SEM Homebrew):**

```bash
./install_simple.sh
```

**Opção 2 - Instalação Completa:**

```bash
./install_ocr.sh
```

Ver guia completo: [INSTALACAO_OCR.md](INSTALACAO_OCR.md)

## 📖 Uso

### 🎼 Tradução de Cifras Individuais

```python
from hermeto_cipher_translator import HermetoTranslator

translator = HermetoTranslator()

# Traduzir cifra para partitura
score = translator.translate("C458/A5+7")
score.show()  # Exibe partitura
score.save("minha_cifra.png")  # Salva como imagem
```

### 🎵 Progressões Harmônicas

```python
from core.progression_processor import HermetoProgressionProcessor

processor = HermetoProgressionProcessor()

# Processar progressão completa
xml_file = processor.export_progression_xml(
    "Am7 | C7+ | F#79+13- | D7+9+11+",
    "progressao.xml",
    tempo_bpm=120,
    show_chord_symbols=True  # Mostra cifras na partitura
)
```

### 📷 OCR de Partituras (NOVO!)

```python
from image_to_score import HermetoImageToScore

converter = HermetoImageToScore()

# Extrair cifras de imagem
progression = converter.image_to_progression_string('partitura.jpg')

# Converter diretamente para MusicXML
xml_file = converter.image_to_musicxml('partitura.jpg')
```

### 🌐 Interface Web

```bash
cd web && python3 app.py
# Acesse: http://localhost:5000
```

## 🎹 Exemplos

- `D7+` → Acorde maior expandido com 7M, 9M, 13M
- `C-479` → Acorde menor distribuído entre as mãos
- `Em7/Ab6` → Tetrade Em7 (direita) + sexta Ab (esquerda)
- `F#79+13-` → Dominante com 9+ e 13-

## 🧪 Testes

```bash
pytest tests/
```

## 📚 Referências

Baseado no sistema de cifragem universal desenvolvido por Hermeto Pascoal, documentado através de análise de vídeos educacionais e materiais de músicos que colaboraram com o mestre.

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.
