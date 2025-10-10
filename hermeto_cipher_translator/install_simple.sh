#!/bin/bash

# Instalação OCR Simplificada (SEM Homebrew)
# Para usuários macOS que não querem usar Homebrew

echo "🎼 Instalação OCR Hermética - Modo Simplificado"
echo "=============================================="
echo "Esta instalação usa apenas Python - não precisa do Tesseract!"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    echo "   Instale Python 3 primeiro: https://python.org/"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Instalar dependências Python básicas
echo "📦 Instalando dependências Python..."
pip3 install opencv-python pillow numpy

# Tentar instalar EasyOCR (alternativa ao Tesseract)
echo ""
echo "🔍 Instalando EasyOCR (pode demorar alguns minutos)..."
echo "   Esta é uma alternativa ao Tesseract que não precisa de instalação sistema"

if pip3 install easyocr; then
    echo "✅ EasyOCR instalado com sucesso!"
    OCR_METHOD="easyocr"
else
    echo "⚠️  EasyOCR falhou. Usando modo básico."
    OCR_METHOD="basic"
fi

echo ""
echo "🧪 Testando instalação..."

# Teste da instalação
python3 << EOF
import sys
import cv2
import numpy as np
from PIL import Image

print("✅ OpenCV: OK")
print("✅ PIL: OK")
print("✅ NumPy: OK")

try:
    import easyocr
    print("✅ EasyOCR: OK - Sistema completo!")
    print("")
    print("🎯 COMO USAR:")
    print("1. Acesse: http://localhost:5000/ocr")
    print("2. Ou use o código Python:")
    print("   from ocr_alternative import HermetoOCRAlternative")
    print("   ocr = HermetoOCRAlternative()")
    print("   results = ocr.process_score_image('imagem.jpg')")
    
except ImportError:
    print("⚠️  EasyOCR: Não disponível")
    print("   Sistema funcionará em modo básico")
    print("")
    print("💡 ALTERNATIVAS:")
    print("1. Instalar Tesseract manualmente:")
    print("   - Baixe de: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   - Ou use Anaconda: conda install tesseract")
    print("")
    print("2. Usar EasyOCR (sem Tesseract):")
    print("   - pip3 install easyocr")

print("")
print("📋 PRÓXIMOS PASSOS:")
print("1. Inicie o servidor: python3 web/app.py")
print("2. Acesse: http://localhost:5000/ocr")
print("3. Carregue imagens de partituras do Hermeto")
EOF

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "🚀 Para iniciar o sistema:"
echo "   cd web && python3 app.py"
echo ""
echo "🌐 Acesse no navegador:"
echo "   http://localhost:5000/ocr"
echo ""

# Perguntar se quer iniciar automaticamente
read -p "Deseja iniciar o servidor agora? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🚀 Iniciando servidor..."
    cd web && python3 app.py
fi