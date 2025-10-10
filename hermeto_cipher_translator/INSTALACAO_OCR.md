# 🔧 Guia de Instalação OCR - Todas as Opções

Este guia apresenta **múltiplas formas** de instalar o sistema OCR, desde a mais simples até a mais completa.

## 🚀 **OPÇÃO 1: Instalação Simplificada (RECOMENDADA)**

**Não precisa do Homebrew, não precisa do Tesseract!**

```bash
# Execute o script simplificado
./install_simple.sh
```

### O que faz:

- ✅ Instala apenas dependências Python
- ✅ Usa EasyOCR (não precisa Tesseract)
- ✅ Funciona sem Homebrew
- ✅ Instalação rápida (5-10 minutos)

---

## 🔧 **OPÇÃO 2: Instalação Manual por Etapas**

### Passo 1: Dependências Python básicas

```bash
pip3 install opencv-python pillow numpy
```

### Passo 2: OCR Engine (escolha uma)

**2A. EasyOCR (Recomendado - sem Tesseract)**

```bash
pip3 install easyocr
```

**2B. Tesseract via Conda/Anaconda**

```bash
conda install -c conda-forge tesseract
pip3 install pytesseract
```

**2C. Tesseract via MacPorts**

```bash
# 1. Instalar MacPorts: https://www.macports.org/
# 2. Depois:
sudo port install tesseract tesseract-por tesseract-eng
pip3 install pytesseract
```

**2D. Tesseract - Download direto**

```bash
# 1. Baixar instalador: https://github.com/UB-Mannheim/tesseract/wiki
# 2. Instalar o .pkg
# 3. Depois:
pip3 install pytesseract
```

---

## 🏗️ **OPÇÃO 3: Instalação Completa (com Homebrew)**

Se você tem ou quer instalar o Homebrew:

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Executar instalação completa
./install_ocr.sh
```

---

## 🧪 **Teste da Instalação**

Execute este código para testar:

```python
python3 << 'EOF'
# Teste básico
try:
    import cv2
    import numpy as np
    from PIL import Image
    print("✅ Dependências básicas: OK")

    # Testar EasyOCR
    try:
        import easyocr
        print("✅ EasyOCR: Disponível")

        # Teste completo
        from ocr_alternative import HermetoOCRAlternative
        ocr = HermetoOCRAlternative()
        print("✅ Sistema OCR: Funcionando!")

    except ImportError:
        print("⚠️  EasyOCR: Não disponível")

        # Testar Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            print("✅ Tesseract: Disponível")

            from ocr_hermeto import HermetoOCR
            ocr = HermetoOCR()
            print("✅ Sistema OCR: Funcionando!")

        except:
            print("❌ Nenhum OCR disponível")
            print("   Execute uma das opções de instalação")

except ImportError as e:
    print(f"❌ Dependências faltando: {e}")
    print("   Execute: pip3 install opencv-python pillow numpy")
EOF
```

---

## 📋 **Comparação das Opções**

| Método        | Facilidade | Velocidade | Precisão   | Dependências     |
| ------------- | ---------- | ---------- | ---------- | ---------------- |
| **EasyOCR**   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | ⭐⭐⭐⭐   | Apenas Python    |
| **Tesseract** | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Sistema + Python |
| **Conda**     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | Anaconda         |
| **MacPorts**  | ⭐⭐       | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | MacPorts         |
| **Homebrew**  | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | Homebrew         |

---

## 🎯 **Recomendação por Situação**

### 🥇 **Para começar rapidamente:**

```bash
./install_simple.sh
```

- Usa EasyOCR
- Não precisa de instalações complexas
- Funciona bem para a maioria dos casos

### 🏆 **Para máxima precisão:**

```bash
# Se tem Anaconda:
conda install -c conda-forge tesseract
pip3 install pytesseract

# Ou se tem Homebrew:
brew install tesseract tesseract-lang
pip3 install pytesseract
```

### 🛠️ **Para desenvolvimento:**

```bash
# Instalar ambos para comparar
pip3 install easyocr pytesseract
# Sistema detecta automaticamente qual usar
```

---

## 🆘 **Solução de Problemas**

### "Tesseract not found"

```bash
# Verificar instalação
which tesseract
tesseract --version

# Se não encontrar, usar EasyOCR:
pip3 install easyocr
```

### "EasyOCR muito lento"

```bash
# EasyOCR é mais lento na primeira execução
# Depois fica mais rápido
# Para velocidade máxima, use Tesseract
```

### "Erro de importação"

```bash
# Instalar dependências básicas
pip3 install opencv-python pillow numpy

# Escolher uma opção de OCR
pip3 install easyocr  # OU
pip3 install pytesseract  # (precisa Tesseract instalado)
```

### "Baixa precisão OCR"

1. Use imagens de boa qualidade
2. Ajuste o parâmetro de confiança (0.2-0.4)
3. Tente diferentes engines (EasyOCR vs Tesseract)

---

## 🚀 **Como Usar Após Instalação**

### Interface Web:

```bash
cd web && python3 app.py
# Acesse: http://localhost:5000/ocr
```

### Via Código:

```python
from image_to_score import HermetoImageToScore

converter = HermetoImageToScore()
progression = converter.image_to_progression_string('partitura.jpg')
xml_file = converter.image_to_musicxml('partitura.jpg')
```

---

**💡 Dica:** Comece com a **Opção 1** (install_simple.sh). Se precisar de mais precisão, depois instale o Tesseract.
