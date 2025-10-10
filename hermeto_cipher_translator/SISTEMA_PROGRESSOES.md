# 🎵 SISTEMA DE PROGRESSÕES HERMÉTICAS

## **🚀 NOVA FUNCIONALIDADE IMPLEMENTADA**

Expandindo o sistema original de acordes individuais, agora você pode:

- **Processar progressões completas** de acordes
- **Gerar partituras MusicXML** de sequências harmônicas
- **Exportar arquivos MIDI** para reprodução
- **Configurar tempo, fórmula de compasso e tonalidade**
- **Analisar estatisticamente** as progressões

---

## **📋 COMO USAR**

### **1. Interface Web (Recomendado)**

```bash
# Iniciar servidor
cd web && python app.py

# Acessar no navegador
http://localhost:5000/progression
```

### **2. Via Código Python**

```python
from core.progression_processor import HermetoProgressionProcessor

processor = HermetoProgressionProcessor()

# Processar progressão
progressao = "Am7 | C7+ | F#79+13- | D7+9+11+"
xml_file = processor.export_progression_xml(
    progressao,
    "minha_progressao.xml",
    tempo=120,
    title="Minha Progressão Hermética"
)
```

### **3. Função Rápida**

```python
from core.progression_processor import process_progression

# Gerar XML e MIDI de uma vez
process_progression(
    "C7+ | F#-5- | Em7/Ab6",
    export_format='both',
    filename='progressao_complexa'
)
```

---

## **🎼 FORMATOS DE INPUT SUPORTADOS**

### **Separação por |**

```
"Am7 | C7+ | F#79+13- | D7+9+11+"
```

### **Separação por espaços**

```
"Am7 C7+ F#79+13- D7+9+11+"
```

### **Separação por compasso (/)**

```
"Am7 / C7+ / F#79+13-"
```

### **Com duração específica**

```
"Am7(2) | C7+(4) | F#79+13-(1)"
```

_(Números entre parênteses = duração em beats)_

---

## **⚙️ CONFIGURAÇÕES DISPONÍVEIS**

| Parâmetro        | Padrão                 | Opções                     | Descrição           |
| ---------------- | ---------------------- | -------------------------- | ------------------- |
| `tempo`          | 120                    | 60-200                     | BPM da música       |
| `time_signature` | "4/4"                  | "4/4", "3/4", "2/4", "6/8" | Fórmula de compasso |
| `key_signature`  | "C"                    | "C", "G", "D", "Am", etc.  | Tonalidade          |
| `title`          | "Progressão Hermética" | String                     | Título da partitura |

---

## **📊 ANÁLISE AUTOMÁTICA**

O sistema gera automaticamente:

```python
{
    'total_acordes': 4,
    'duracao_total_beats': 16.0,
    'duracao_media_por_acorde': 4.0,
    'tipos_acordes': {
        'menor': 1,
        'maior': 2,
        'dominante': 1
    },
    'sequencia_acordes': ['Am7', 'C7+', 'F#79+13-', 'D7+9+11+'],
    'complexidade_media': 3.2
}
```

---

## **🎯 EXEMPLOS PRÁTICOS**

### **Progressão de Jazz Hermética**

```python
progressao_jazz = "Am7 | C7+ | F#79+13- | D7+9+11+"
# Gera: La menor 7ª → Dó maior expandido → Fá# dominante alterado → Ré dominante com tensões
```

### **Sequência Experimental**

```python
progressao_experimental = "C7+ | F#-5- | Em7/Ab6"
# Gera: Dó maior expandido → Fá# meio-diminuto → Mi menor 7ª sobre Lá♭ 6ª
```

### **Progressão com Ritmo**

```python
progressao_ritmica = "G458(1) | C7+(2) | Am7(4) | D7+(1)"
# Diferentes durações: 1 beat, 2 beats, 4 beats, 1 beat
```

---

## **💾 FORMATOS DE EXPORT**

### **MusicXML** (.xml)

- Formato padrão internacional
- Compatível com MuseScore, Finale, Sibelius
- Mantém informações de claves, tempo, tonalidade
- Perfeito para edição posterior

### **MIDI** (.mid)

- Formato de áudio digital
- Reproduzível em qualquer DAW
- Mantém informações de tempo e duração
- Ideal para produção musical

---

## **🌐 INTERFACE WEB COMPLETA**

A interface web inclui:

✅ **Input intuitivo** com validação em tempo real  
✅ **Configurações avançadas** (tempo, compasso, tonalidade)  
✅ **Análise visual** com gráficos e estatísticas  
✅ **Visualização dos acordes** com notas por mão  
✅ **Export direto** para XML e MIDI  
✅ **Exemplos pré-carregados** para aprendizado  
✅ **Design responsivo** para mobile/desktop

### **Capturas de Tela**

- **Input**: Campo de texto com exemplos clicáveis
- **Configurações**: Painel com tempo, compasso, tonalidade
- **Análise**: Estatísticas automáticas da progressão
- **Resultado**: Lista visual dos acordes processados
- **Export**: Botões para download XML/MIDI

---

## **🔧 ARQUITETURA TÉCNICA**

### **Módulos Principais**

```
progression_processor.py
├── HermetoProgressionProcessor (classe principal)
├── ProgressionChord (dataclass)
├── parse_progression_string() (parsing de input)
├── process_progression() (processamento completo)
├── generate_musicxml_progression() (geração XML)
├── export_progression_midi() (geração MIDI)
└── analyze_progression() (análise estatística)
```

### **Integração com Sistema Existente**

- **Reutiliza** toda a lógica de acordes individuais
- **Estende** para sequências harmônicas
- **Mantém** compatibilidade total
- **Adiciona** funcionalidades de tempo e estrutura

### **Fluxo de Processamento**

1. **Parse** da string de progressão
2. **Conversão** de cada acorde individualmente
3. **Estruturação** temporal (compassos, beats)
4. **Geração** de partitura completa
5. **Export** nos formatos desejados

---

## **🎓 VALOR PARA TCC**

### **Funcionalidade Avançada**

- Evolução natural do sistema original
- Complexidade técnica aumentada
- Aplicação prática mais robusta

### **Casos de Uso Reais**

- **Músicos**: Converter progressões herméticas completas
- **Pesquisadores**: Analisar sequências harmônicas
- **Educadores**: Demonstrar progressões complexas
- **Produtores**: Gerar bases MIDI para gravação

### **Métricas de Validação**

- Testar com progressões reais do Hermeto Pascoal
- Validar com músicos especialistas
- Benchmark de performance para sequências longas
- Análise estatística de corpus de progressões

---

## **🚀 PRÓXIMOS PASSOS**

### **Para uso imediato:**

1. **Teste** a interface web em `/progression`
2. **Experimente** com suas próprias progressões
3. **Exporte** arquivos XML/MIDI para seu software musical
4. **Documente** casos de uso interessantes

### **Para expansão do TCC:**

1. **Catalogar** progressões reais das obras do Hermeto
2. **Analisar** padrões estatísticos de sequências
3. **Validar** com especialistas em música
4. **Comparar** com progressões de outros compositores

---

**🎵 Sistema completo e funcional, pronto para uso profissional e acadêmico!**
