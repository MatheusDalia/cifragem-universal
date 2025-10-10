#!/usr/bin/env python3
"""
Exemplo de uso do Tradutor de Cifras Herméticas
Execute este arquivo para testar diferentes cifras
"""

from core.hermeto_translator import HermetoTranslator
import sys
import os

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("Cifragem Universal: Tradutor de Cifras Herméticas")
    print("=" * 55)

    # Inicializar tradutor
    translator = HermetoTranslator()

    # Cifras de exemplo para testar
    cifras_exemplo = [
        "D7+",      # Maior expandido
        "C-479",    # Menor com distribuição
        "A/F6",     # Sobreposto simples
        "Em7/Ab6",  # Tétrade sobreposta
        "F 4 7 9",  # Suspenso
        "G#-5-",    # Meio-diminuto
        "F#79+13-"  # Dominante alterado
    ]

    for cifra in cifras_exemplo:
        print(f"\n🎵 Cifra: {cifra}")
        print("-" * 30)

        try:
            # Obter informações da cifra
            info = translator.get_chord_info(cifra)

            print(f"Tipo: {info['type']}")
            print(f"Total de notas: {info['total_notes']}")

            # Mostrar distribuição
            direita = [
                f"{note.name}{note.octave}" for note in info['right_hand']]
            esquerda = [
                f"{note.name}{note.octave}" for note in info['left_hand']]

            print(
                f"Mão direita (Clave Sol): {direita if direita else 'Vazia'}")
            print(
                f"Mão esquerda (Clave Fá): {esquerda if esquerda else 'Vazia'}")

        except Exception as e:
            print(f"❌ Erro ao processar '{cifra}': {e}")

    print("\n" + "=" * 55)
    print("✅ Teste concluído!")
    print("\nPara testar mais cifras:")
    print("1. Interface web: http://127.0.0.1:5000")
    print("2. Modifique este arquivo com suas cifras")
    print("3. Use o translator.get_chord_info('SUA_CIFRA')")


def testar_cifra_interativa():
    """Função para testar uma cifra específica"""
    translator = HermetoTranslator()

    print("\n🎼 Teste Interativo de Cifras")
    print("Digite uma cifra hermética (ou 'sair' para encerrar):")

    while True:
        cifra = input("\nCifra > ").strip()

        if cifra.lower() in ['sair', 'exit', 'quit', '']:
            break

        try:
            info = translator.get_chord_info(cifra)

            print(f"\n✅ Resultado para '{cifra}':")
            print(f"   Tipo: {info['type']}")

            direita = [
                f"{note.name}{note.octave}" for note in info['right_hand']]
            esquerda = [
                f"{note.name}{note.octave}" for note in info['left_hand']]

            print(f"   Direita: {direita}")
            print(f"   Esquerda: {esquerda}")

        except Exception as e:
            print(f"❌ Erro: {e}")

    print("👋 Até mais!")


if __name__ == "__main__":
    # Executar exemplos
    main()

    # Perguntar se quer teste interativo
    resposta = input(
        "\nDeseja testar cifras interativamente? (s/n): ").strip().lower()
    if resposta in ['s', 'sim', 'y', 'yes']:
        testar_cifra_interativa()
