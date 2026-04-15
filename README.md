# AudioToLights

AudioToLights is an intelligent, hardware-agnostic system that bridges the gap between music production and automated theatrical lighting control. It utilizes local Generative AI (LLMs) to analyze rhythmic layouts off an audio+MIDI timeline and synthetically choreograph a dynamic DMX lighting show.





## Features
- **AI-Driven Scenography**: Feeds structural MIDI events to a local LLM via Ollama (e.g., Llama 3.2). The LLM acts as an autonomous lighting designer, assigning precise DMX operations based on musical energy.
- **Hardware Integration**: Dynamically parses real-world QLC+ stage files (`.qxfl`), adjusting itself automatically to your venue's equipment (Wash, Beams, Fresnels, LED Bars) without manual hardcoding.
- **Natural Language Control**: Includes a Chat-Refinement UI where technicians can override lighting behaviors with natural language (e.g. "Dim everything to 0 for the first 10 seconds"). 
- **Art-Net Translation**: In-house mapping engine computes specific footprint behaviors like Color Wheel simulation for ATOMIC BEAM 7Rs and pixel mapping for 18-channel LED strips, forwarding all events natively via Art-Net UDP protocol (0.0.0.0:6454).
- **Web-based Control Board**: Real-time synchronous playback and visualization through a single-page Streamlit application.

## System Architecture

```mermaid
graph TD
    %% Frontend / User Input
    subgraph Streamlit Interface ["Frontend (app.py)"]
        UI_Dash[Control Dashboard]
        UI_Chat[Chat Refinement]
        Audio_In[Audio / MIDI Input]
    end

    %% Parsers
    subgraph Parsers ["Data Extraction Layer"]
        MIDI_Pars[MidiParser<br>src/midi_parser.py]
        XML_Pars[FixtureParser<br>src/fixtures.py]
    end
    
    %% AI Core
    subgraph AI ["AI Brain (Ollama)"]
        LLM_Model[Local LLM<br>llama3.2]
        AI_Analy[AIAnalyzer<br>src/ai_analyzer.py]
    end

    %% Engine
    subgraph Playback_Engine ["Core Playback System"]
        PyGame[Audio Playback<br>PyGame Thread]
        Mapper[Event Mapper<br>src/mapping.py]
        Dispatch[DMX Dispatcher<br>src/playback.py]
    end

    %% Network & Hardware
    subgraph Network ["Output Layer"]
        ArtNet[ArtNetSender<br>src/artnet_sender.py]
        QLC[QLC+ Lighting Controller]
        DMX[USB-DMX Interface]
        Lights((Theater Fixtures))
    end

    %% Connections
    Audio_In --> MIDI_Pars
    UI_Dash --> PyGame
    UI_Chat --> AI_Analy
    
    XML_File[(fixtures_teatro.qxfl)] --> XML_Pars
    
    MIDI_Pars -- Timeline Events --> AI_Analy
    XML_Pars -- Hardware Specs --> AI_Analy
    
    AI_Analy -- Prompts --> LLM_Model
    LLM_Model -- JSON Script --> AI_Analy
    
    AI_Analy -- Compiled Script --> Mapper
    PyGame -- Live Sync Tick --> Mapper
    
    Mapper -- Raw Actions --> Dispatch
    Dispatch -- DMX Values --> ArtNet
    
    ArtNet -- UDP 6454 --> QLC
    QLC -- Passthrough --> DMX
    DMX --> Lights
```


## Requirements
- `Python 3.10+`
- `Ollama` installed and running locally with the target model (default: `llama3.2`)
- Required Python modules: 
  ```bash
  pip install -r requirements.txt
  ```
  *(Packages: streamlit, pygame, mido, requests, python-dotenv)*

## Getting Started
1. Start Ollama locally.
2. Ensure your QLC+ venue file is exported to `fixtures_teatro.qxfl` in the root folder.
3. Launch the Control Board:
   ```bash
   start_app.bat
   ```
4. Upload your Audio track (`.MP3`/`.WAV`) and matching Timeline (`.MID`).
5. Click **Generate Colors and Dynamics**.
6. Turn on QLC+ with Art-Net Input and your DMX-USB adapter output.
7. Click **LIVE PLAY**!
