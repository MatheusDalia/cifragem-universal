#!/bin/bash

# Script de instalação do Tradutor de Cifras Herméticas
# Para macOS/Linux

echo "🎼 Instalando Tradutor de Cifras Herméticas do Hermeto Pascoal"
echo "=============================================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv .venv

# Ativar ambiente virtual  
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip

# Instalar dependências principais
pip install music21 flask matplotlib pandas pytest

# Instalar o projeto em modo desenvolvimento
echo "🚀 Instalando projeto..."
pip install -e .

# Configurar music21 (opcional)
echo "🎵 Configurando music21..."
python -c "
import music21
env = music21.environment.Environment()
print('Music21 configurado com sucesso!')
"

# Testar instalação
echo "🧪 Testando instalação..."
python test_translator.py

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "Para usar o tradutor:"
echo "1. Ative o ambiente: source .venv/bin/activate"
echo "2. Interface web: python web/app.py"
echo "3. Teste direto: python test_translator.py"
echo ""
echo "Acesse http://localhost:5000 para a interface web"