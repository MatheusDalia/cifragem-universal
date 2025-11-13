```mermaid
graph TD
    %% Entrada do Usuario
    A[Usuario] --> B{Tipo de Entrada}
    B -->|Texto| C[Cifra Universal<br/>Ex: C7+]
    B -->|Progressao| D[Sequencia de Acordes<br/>Ex: C7+ | Am7 | F7]
    B -->|Imagem| E[Manuscrito<br/>Partitura/Anotacao]

    %% Interface Web
    C --> F[app.py<br/>Flask Web Interface]
    D --> F

    %% OCR Processing
    E --> G[ocr_ai_vision.py<br/>OCR com IA]
    G -->|Texto Extraido| O[progression_processor.py<br/>Processa Progressao]

    %% Coordenador Central
    F --> I[hermeto_translator.py<br/>Coordenador Central]
    O --> I

    %% Pipeline de Processamento Core
    I --> J[chord_parser.py<br/>Parse de Cifras]
    J --> K[interval_converter.py<br/>Simbolos para Intervalos]
    K --> L[note_generator.py<br/>Intervalos para Notas]
    L --> M[staff_distributor.py<br/>Distribuicao Claves]
    M --> N[score_generator.py<br/>Gerador de Partitura]

    %% Saidas para Acordo Isolado
    N -->|Acordo Isolado| P1{Saidas Acorde}
    P1 --> Q1[MusicXML Download]
    P1 --> R1[MIDI Download]
    P1 --> S1[PNG Partitura Web]
    P1 --> T1[Player Audio Web]
    P1 --> U1[JSON Dados]

    %% Saidas para Progressao
    O -->|Progressao| P2{Saidas Progressao}
    P2 --> Q2[MusicXML Download]
    P2 --> R2[MIDI Download]
    P2 --> U2[JSON Dados]

    %% Bibliotecas Externas
    N --> V[Music21<br/>Biblioteca Musical]
    G --> W[APIs de IA<br/>GPT-4/Gemini/Claude]

    %% Estilos
    classDef entrada fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef processamento fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef saida fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef externo fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class A,B,C,D,E entrada
    class F,I,J,K,L,M,N,O,G processamento
    class P1,P2,Q1,Q2,R1,R2,S1,T1,U1,U2 saida
    class V,W externo
```

# Fluxograma da Arquitetura do Sistema de Cifragem Universal

## Visão Geral

O sistema é composto por módulos especializados que processam cifras universais de Hermeto Pascoal de forma sequencial e integrada.

## Legenda Detalhada dos Componentes

### 🔵 Camada de Dados (Azul)

- **chord_dictionary.py**: Base de conhecimento com mapeamentos cifra→intervalos, extensões automáticas, 200+ variações harmônicas
- **Sistema de Validação**: Verifica integridade dos dados entre módulos, detecta inconsistências, garante qualidade do processamento

### 🟠 Camada de Processamento (Laranja)

- **app.py**: Interface web Flask principal, gerencia requisições HTTP, coordena formatos de saída, endpoints REST
- **ocr_ai_vision.py**: Reconhecimento inteligente de manuscritos usando GPT-4 Vision, Gemini Pro Vision, Claude Vision
- **hermeto_translator.py**: Coordenador central que orquestra pipeline completo, valida dados entre etapas, controla fluxo
- **chord_parser.py**: Interpreta sintaxe das cifras, separa fundamental/tensões/sobreposições, detecta tipos de acordo
- **interval_converter.py**: Converte símbolos herméticos (+/-/números) em intervalos musicais precisos, aplica extensões automáticas
- **note_generator.py**: Transforma intervalos em notas absolutas com nome, oitava, número MIDI, calcula enarmônias
- **staff_distributor.py**: Organiza notas entre mãos (direita/esquerda) e claves (Sol/Fá), otimiza ergonomia pianística
- **score_generator.py**: Gera partitura visual usando Music21, cria representação MusicXML/MIDI final
- **progression_processor.py**: Processa sequências de acordes extraídas do OCR, organiza compassos, gerencia timing

### 🟢 Camada de Saída (Verde)

#### **Saídas para Acorde Isolado:**

- **MusicXML Download**: Arquivo para download, compatível com Finale, Sibelius, MuseScore
- **MIDI Download**: Arquivo para download, compatível com DAWs e teclados controladores
- **PNG Partitura Web**: Visualização da partitura diretamente no navegador
- **Player Audio Web**: Reprodução do acorde no navegador para audição
- **JSON Dados**: Informações estruturadas (notas, intervalos, MIDI, enarmônicos)

#### **Saídas para Progressão de Acordes:**

- **MusicXML Download**: Arquivo para download da progressão completa
- **MIDI Download**: Arquivo para download da sequência de acordes
- **JSON Dados**: Array de acordes + análise harmônica + configurações temporais

### 🔴 Bibliotecas Externas (Rosa)

- **📚 Music21**: Biblioteca Python para processamento musical, geração de partituras, análise harmônica
- **🤖 APIs de IA**: OpenAI GPT-4 Vision, Google Gemini, Anthropic Claude para OCR avançado

## Tipos de Saída JSON

### **1. JSON para Acordo Isolado (endpoint: `/translate`)**

```json
{
  "success": true,
  "cipher": "C7+",
  "translation": {
    "original": "C7+",
    "type": "maior com sétima maior",
    "left_hand": [
      { "name": "C", "octave": 3, "midi_number": 48, "enharmonic": "C" }
    ],
    "right_hand": [
      { "name": "E", "octave": 4, "midi_number": 64, "enharmonic": "E" },
      { "name": "G", "octave": 4, "midi_number": 67, "enharmonic": "G" }
    ],
    "intervals": [
      { "name": "1ª justa", "semitones": 0, "degree": 1 },
      { "name": "3ª maior", "semitones": 4, "degree": 3 }
    ],
    "total_notes": 3
  }
}
```

### **2. JSON para Progressão (endpoint: `/progression`)**

```json
{
  "success": true,
  "progression": "C7+ | Am7",
  "chords": [
    {
      "original_cipher": "C7+",
      "chord_type": "maior com sétima maior",
      "left_hand_notes": [{ "name": "C", "octave": 3 }],
      "right_hand_notes": [{ "name": "E", "octave": 4 }],
      "duration": 4,
      "bar": 1,
      "beat": 1
    }
  ],
  "analysis": {
    "total_acordes": 2,
    "duracao_total_beats": 8,
    "tipos_acordes": { "maior": 1, "menor": 1 }
  },
  "settings": {
    "tempo": 120,
    "time_signature": "4/4",
    "key_signature": "C",
    "title": "Progressão Hermética"
  }
}
```

## Fluxo de Dados Detalhado

### 1. **Entrada → Parsing**

```
Usuário digita: "C7+"
↓
ChordParser: { root: "C", chord_type: "maior", intervals: ["7+"] }
```

### 2. **Parsing → Intervalos**

```
IntervalConverter recebe: { chord_type: "maior", intervals: ["7+"] }
↓
Gera: [1ª justa, 3ª maior, 5ª justa, 7ª maior, 9ª maior, 13ª maior]
```

### 3. **Intervalos → Notas**

```
NoteGenerator recebe: intervalos + root "C"
↓
Gera: [C4, E4, G4, B4, D5, A5]
```

### 4. **Notas → Distribuição**

```
StaffDistributor recebe: [C4, E4, G4, B4, D5, A5]
↓
Mão esquerda: [C3, E3, G3] | Mão direita: [B4, D5, A4]
```

### 5. **Distribuição → Partitura**

```
ScoreGenerator recebe: notas por mão
↓
Gera: Partitura com clave de Sol/Fá, exportável em múltiplos formatos
```

## Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Flask**: Framework web para interface
- **Music21**: Processamento e geração musical
- **APIs de IA**: GPT-4/Gemini/Claude para OCR
- **Mermaid**: Diagramação da arquitetura
