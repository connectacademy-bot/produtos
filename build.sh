#!/bin/bash
echo "🚀 Iniciando build..."

pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependências instaladas com sucesso."
echo "🚀 Iniciando bot..."
python bot.py
