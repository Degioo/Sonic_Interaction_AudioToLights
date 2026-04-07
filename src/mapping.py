class Mapper:
    def __init__(self, ai_script=None):
        # Il copione generato dall'AI, se presente, conterrà le azioni pre-calcolate
        self.ai_script = ai_script
        
    def process_event(self, event):
        """
        Takes an event dict: {"t": float, "note": int, "velocity": int}
        and returns a list of OSC actions to perform.
        """
        note = event["note"]
        velocity = event["velocity"]
        t = event["t"]
        
        # --- BLOCCO AI ---
        # Se abbiamo il copione dell'AI, cerchiamo l'azione decisa per questo istante 't'
        if self.ai_script:
            for action in self.ai_script:
                # Controlliamo la corrispondenza dell'evento al millesimo
                if abs(action.get("t", -1) - t) < 0.001:
                    return [action]

        # --- FALLBACK DI SICUREZZA (Rule-Based Classico se niente AI) ---
        # Scale velocity 0-127 to 0-255 for DMX intensity
        intensity = int((velocity / 127.0) * 255)

        
        actions = []
        
        if note < 55:
            # Low register -> PAR, warm color
            # We will alternate between par_1 and par_2 for variety, or just hit both.
            actions.append({
                "target": "par",
                "id": "par_1",  # Could be dynamic later
                "intensity": intensity,
                "color": (255, 100, 0) # Warm orange/red
            })
            actions.append({
                "target": "par",
                "id": "par_2",  
                "intensity": intensity,
                "color": (255, 50, 0) # Warm red
            })
            
        elif 55 <= note < 76:
            # Mid register -> Moving Head, cool/intermediate color, pan/tilt based on note
            # Let's map note 55-75 to pan 0-255 loosely.
            pan = int(((note - 55) / 20.0) * 255)
            tilt = 127 # fixed tilt for now
            
            actions.append({
                "target": "moving_head",
                "id": "mh_1",
                "intensity": intensity,
                "color": (0, 150, 255), # Cool blue
                "pan": pan,
                "tilt": 127
            })
            actions.append({
                "target": "moving_head",
                "id": "mh_2",
                "intensity": intensity,
                "color": (50, 200, 255), # Cool cyan
                "pan": 255 - pan, # Mirrored pan
                "tilt": 127
            })
            
        else:
            # High register -> Strobe
            # High intensity, strobe rate from velocity
            actions.append({
                "target": "strobe",
                "id": "strobe_1",
                "intensity": 255, # Max intensity for strobe blast
                "rate": intensity # Rate scales with velocity
            })
            
        return actions
