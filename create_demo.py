import pretty_midi
import os

def create_demo_midi():
    # Make sure data dir exists
    os.makedirs('data', exist_ok=True)
    
    # Create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()
    
    # Create an Instrument instance for a piano instrument
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)
    
    # Add some low notes (PARs)
    piano.notes.append(pretty_midi.Note(velocity=100, pitch=40, start=0.0, end=0.5))
    piano.notes.append(pretty_midi.Note(velocity=100, pitch=45, start=1.0, end=1.5))
    
    # Add some mid notes (Moving Heads)
    piano.notes.append(pretty_midi.Note(velocity=110, pitch=60, start=2.0, end=2.5))
    piano.notes.append(pretty_midi.Note(velocity=110, pitch=65, start=2.5, end=3.0))
    piano.notes.append(pretty_midi.Note(velocity=110, pitch=70, start=3.0, end=3.5))
    
    # Add some high notes (Strobe)
    piano.notes.append(pretty_midi.Note(velocity=127, pitch=80, start=4.0, end=4.2))
    piano.notes.append(pretty_midi.Note(velocity=127, pitch=85, start=4.5, end=4.7))
    piano.notes.append(pretty_midi.Note(velocity=127, pitch=90, start=5.0, end=5.2))
    
    # Mix registers together to see simultaneous actions
    piano.notes.append(pretty_midi.Note(velocity=120, pitch=40, start=6.0, end=6.5))
    piano.notes.append(pretty_midi.Note(velocity=120, pitch=65, start=6.0, end=6.5))
    piano.notes.append(pretty_midi.Note(velocity=120, pitch=80, start=6.0, end=6.5))
    
    # Add the single instrument to the PrettyMIDI object
    midi.instruments.append(piano)
    
    # Write out the MIDI data
    midi.write('data/demo.mid')
    print("demo.mid created successfully!")

if __name__ == "__main__":
    create_demo_midi()
