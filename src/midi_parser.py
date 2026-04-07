import mido

class MidiParser:
    def __init__(self, midi_path):
        self.midi_path = midi_path
        self.events = []

    def parse(self):
        """
        Reads the MIDI file and extracts note_on events.
        Produces a chronological list of events with absolute time in seconds.
        """
        mid = mido.MidiFile(self.midi_path)
        current_time_seconds = 0.0
        
        for msg in mid:
            # mid yields messages with delta times in seconds.
            current_time_seconds += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                self.events.append({
                    "t": float(current_time_seconds),
                    "note": msg.note,
                    "velocity": msg.velocity
                })
                
        return self.events
