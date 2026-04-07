import os
from src.osc_sender import OSCSender
from src.midi_parser import MidiParser
from src.mapping import Mapper
from src.playback import PlaybackEngine
from src.ai_analyzer import AIAnalyzer
from src.fixtures import FIXTURES
import tkinter as tk
from tkinter import filedialog
import os
import pygame

def main():
    print("Starting sid-midi-lights...")
    
    # 0. Scegli il file MIDI visivamente
    root = tk.Tk()
    root.withdraw() # nasconde la finestra vuota principale
    print("Seleziona una canzone MIDI dalla finestra di dialogo...")
    midi_path = filedialog.askopenfilename(
        title="Seleziona la tua canzone MIDI",
        filetypes=[("MIDI files", "*.mid *.midi"), ("All files", "*.*")]
    )
    
    if not midi_path:
        print("Nessun file selezionato, cerco data/demo.mid di default...")
        midi_path = os.path.join("data", "demo.mid")
        
    print(f"1. Parsing MIDI file: {midi_path}")
    parser = MidiParser(midi_path)
    events = parser.parse()
    print(f"Found {len(events)} note_on events.")
    
    # 2. Inizializza l'Intelligenza Artificiale
    print("2. Caricamento AI Gemini...")
    analyzer = AIAnalyzer()
    ai_script = analyzer.generate_lighting_script(events, FIXTURES)
    
    if ai_script:
        print("L'AI ha creato la scenografia!")
    else:
        print("Scenografia AI non disponibile, uso regole standard.")
    
    print("3. Connecting to OSC (QLC+ on localhost:7700)...")
    sender = OSCSender(ip="127.0.0.1", port=7700)
    
    print("4. Initializing Mapper and Playback Engine...")
    mapper = Mapper(ai_script=ai_script)
    playback = PlaybackEngine(sender, mapper)
    
    # Inizializza il motore audio per farti sentire la canzone!
    print("5. Inizializzo il lettore audio (Pygame)...")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(midi_path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Errore audio, i suoni o i midi driver del sistema potrebbero non essere attivi: {e}")
    
    print("\n--- Starting Playback ---")
    playback.play(events)  # Questo mette in play le luci, allineato con l'audio!
    print("--- Playback Complete ---")
    
    # Ferma la musica alla fine delle luci
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()

if __name__ == "__main__":
    main()
