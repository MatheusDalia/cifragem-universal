#!/bin/bash

# Script de instalação das dependências OCR
# Para o sistema de reconhecimento de cifras herméticas

echo "🔍 Instalando dependências OCR para Cifras Herméticas"
echo "===================================================="

# Verificar sistema operacional
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detectado: macOS"
    
    # Tentar múltiplas opções de instalação
    if command -v brew &> /dev/null; then
        echo "📥 Opção 1: Instalando via Homebrew..."
        brew install tesseract tesseract-lang
        
    elif command -v port &> /dev/null; then
        echo "📥 Opção 2: Instalando via MacPorts..."
        sudo port install tesseract tesseract-por tesseract-eng
        
    else
        echo "🔧 Instalação manual necessária"
        echo ""
        echo "📋 OPÇÕES DE INSTALAÇÃO SEM HOMEBREW:"
        echo ""
        echo "1️⃣  INSTALAÇÃO VIA CONDA/ANACONDA:"
        echo "    conda install -c conda-forge tesseract"
        echo ""
        echo "2️⃣  DOWNLOAD DIRETO (RECOMENDADO):"
        echo "    https://github.com/UB-Mannheim/tesseract/wiki"
        echo "    Baixe o instalador .pkg para macOS"
        echo ""
        echo "3️⃣  VIA MACPORTS:"
        echo "    - Instale MacPorts: https://www.macports.org/"
        echo "    - Execute: sudo port install tesseract"
        echo ""
        echo "4️⃣  COMPILAR DO CÓDIGO FONTE:"
        echo "    - Veja instruções em: https://tesseract-ocr.github.io/tessdoc/Compiling.html"
        echo ""
        echo "⚡ SOLUÇÃO RÁPIDA - Usar Python puro:"
        echo "   pip install easyocr  # Alternativa que não precisa do Tesseract"
        echo ""
        
        # Perguntar qual opção o usuário prefere
        echo "Escolha uma opção (1-4) ou pressione Enter para tentar Python puro:"
        read -r option
        
        case $option in
            1)
                echo "📦 Verificando se conda está disponível..."
                if command -v conda &> /dev/null; then
                    conda install -c conda-forge tesseract
                else
                    echo "❌ Conda não encontrado. Instale Anaconda/Miniconda primeiro"
                fi
                ;;
            2)
                echo "🌐 Abrindo página de download..."
                open "https://github.com/UB-Mannheim/tesseract/wiki"
                echo "⏳ Aguardando instalação manual..."
                echo "   Pressione Enter quando terminar a instalação"
                read -r
                ;;
            3)
                echo "🌐 Abrindo página do MacPorts..."
                open "https://www.macports.org/"
                echo "⏳ Instale MacPorts e depois execute:"
                echo "   sudo port install tesseract tesseract-por tesseract-eng"
                echo "   Pressione Enter quando terminar"
                read -r
                ;;
            4)
                echo "🌐 Abrindo guia de compilação..."
                open "https://tesseract-ocr.github.io/tessdoc/Compiling.html"
                echo "⏳ Siga as instruções de compilação"
                echo "   Pressione Enter quando terminar"
                read -r
                ;;
            *)
                echo "🐍 Tentando alternativa Python pura..."
                pip install easyocr
                echo "✅ EasyOCR instalado como alternativa"
                ;;
        esac
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detectado: Linux"
    
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        echo "📥 Instalando Tesseract via apt-get..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-por tesseract-ocr-eng
        sudo apt-get install -y libtesseract-dev
        
    # CentOS/RHEL
    elif command -v yum &> /dev/null; then
        echo "📥 Instalando Tesseract via yum..."
        sudo yum install -y tesseract tesseract-langpack-por tesseract-langpack-eng
        
    else
        echo "⚠️  Gerenciador de pacotes não suportado"
        echo "   Instale manualmente o Tesseract OCR"
    fi
    
else
    echo "⚠️  Sistema operacional não suportado automaticamente"
    echo "   Instale manualmente o Tesseract OCR"
fi

# Instalar dependências Python
echo "🐍 Instalando dependências Python..."
pip install opencv-python pytesseract pillow numpy scikit-learn

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "🧪 Testando instalação..."

# Teste básico
python3 << 'EOF'
try:
    import cv2
    import pytesseract
    from PIL import Image
    import numpy as np
    
    # Testar Tesseract
    version = pytesseract.get_tesseract_version()
    print(f"✅ Tesseract versão: {version}")
    
    # Testar OpenCV
    cv_version = cv2.__version__
    print(f"✅ OpenCV versão: {cv_version}")
    
    print("✅ Todas as dependências instaladas com sucesso!")
    print("")
    print("🎯 Para usar o OCR:")
    print("   1. Acesse: http://localhost:5000/ocr")
    print("   2. Carregue imagens de partituras do Hermeto")
    print("   3. Ajuste a confiança conforme necessário")
    print("   4. Clique em 'Processar OCR'")
    
except ImportError as e:
    print(f"❌ Erro na instalação: {e}")
    print("   Execute novamente o script ou instale manualmente")
except Exception as e:
    print(f"⚠️  Possível problema: {e}")
    print("   OCR pode funcionar mesmo assim")
EOF