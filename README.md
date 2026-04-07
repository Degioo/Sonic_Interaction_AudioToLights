# AudioToLights

## Sonic Interaction Design

**AudioToLights** is an automated system developed for the "Sonic Interaction Design" course that synchronizes a real-time light show with an audio track execution (MIDI file).

The system leverages Generative AI (Gemini 2.5 Flash) to analyze musical parameter events from a MIDI input and generates a complex visual interpretation, translating it into commands for QLC+ lighting fixtures via the OSC protocol.

## System Architecture

The software architecture consists of five main modules:
1. **MIDI Parser (`MidiParser`)**: Reads and analyzes MIDI files (`.mid`), extracting note events such as Pitch, Velocity, and Rhythm.
2. **AI Analyzer (`AIAnalyzer`)**: Queries the Gemini 2.5 Flash LLM model by passing the extracted MIDI events to generate a creative lighting mapping in a specific JSON format.
3. **Mapper**: Assigns and translates the AI instructions into valid commands for the active QLC+ lighting equipment (e.g., PARs, Moving Heads, Strobes).
4. **OSC Sender (`OSCSender`)**: Handles local network communication using the OSC (Open Sound Control) protocol, sending structured signals to a local QLC+ instance running on port 7700.
5. **Playback Engine (`PlaybackEngine`)**: Ensures time synchronization and parallel playback execution of the audio track (using `pygame`) and the generated OSC light commands.

## AI Integration

Unlike fixed "rule-based" algorithms, the AI approach produces complex and compositional results. The system sends a structured prompt containing the chronological list of events and available rig fixtures to Gemini. The LLM processes rhythmic variations and pitch shifts to assign appropriate light types while modulating intensity based on note velocity.
