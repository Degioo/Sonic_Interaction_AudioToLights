import random

class Mapper:
    def __init__(self, ai_script=None, fixtures=None):
        self.ai_script = ai_script
        self.fixtures = fixtures if fixtures else []
        
        self.pars = [f["id"] for f in self.fixtures if f["type"] == "rgb_par"]
        self.mheads = [f["id"] for f in self.fixtures if f["type"] == "moving_head"]
        self.strobes = [f["id"] for f in self.fixtures if f["type"] == "strobe"]
        self.lasers = [f["id"] for f in self.fixtures if f["type"] == "laser"]
        self.scanners = [f["id"] for f in self.fixtures if f["type"] == "scanner"]
        self.bars = [f["id"] for f in self.fixtures if f["type"] == "led_bar"]
    def process_event(self, event):
        """
        Takes an event dict: {"t": float, "note": int, "velocity": int}
        and returns a list of OSC actions to perform.
        """
        note = event["note"]
        velocity = event["velocity"]
        t = event["t"]
        
        # --- AI BLOCK ---
        # If we have an AI script, look for the action assigned to this timestamp 't'
        ai_list = self.ai_script
        if isinstance(ai_list, dict):
            # If the LLM hallucinated a wrapped JSON object or a single event dictionary
            ai_list = ai_list.get("events", [ai_list])
            
        if ai_list and isinstance(ai_list, list):
            matched_actions = []
            for action in ai_list:
                # 50ms tolerance for LLM float rounding
                if isinstance(action, dict) and abs(action.get("t", -1) - t) < 0.05:
                    matched_actions.append(action)
            
            if matched_actions:
                return matched_actions

        # --- SAFETY FALLBACK (Classic Rule-Based if AI is absent) ---
        # Scale velocity 0-127 to 0-255 for DMX intensity
        intensity = int((velocity / 127.0) * 255)

        
        actions = []
        
        if note < 50:
            for pid in self.pars[:8]:
                actions.append({"target": "rgb_par", "id": pid, "intensity": intensity, "color": (255, 50, 0)})
            for bid in self.bars:
                actions.append({"target": "led_bar", "id": bid, "intensity": intensity, "color": (255, 0, 0)})
                
        elif 50 <= note < 76:
            pan = int(((note - 50) / 26.0) * 255)
            for mhid in (random.sample(self.mheads, 4) if len(self.mheads)>=4 else self.mheads):
                actions.append({
                    "target": "moving_head", "id": mhid, 
                    "intensity": intensity, "color": (0, 150, 255),
                    "pan": pan, "tilt": 127 + random.randint(-40, 40)
                })
            for pid in (random.sample(self.pars, 6) if len(self.pars)>=6 else self.pars):
                actions.append({"target": "rgb_par", "id": pid, "intensity": intensity, "color": (0, 255, 255)})
            
        else:
            for bid in self.bars:
                actions.append({"target": "led_bar", "id": bid, "intensity": intensity, "color": (200, 255, 255)})
            for mhid in self.mheads:
                actions.append({
                    "target": "moving_head", "id": mhid,
                    "intensity": intensity, "pan": random.randint(0,255), "tilt": random.randint(0,255), "color": (255,255,255)
                })
            
        return actions
