import os
import json
import requests
from dotenv import load_dotenv

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key or self.api_key == "inserisci_qui_la_tua_chiave":
            print("[ATTENZIONE] Nessuna API KEY Gemini valida trovata nel file .env!")
            self.model = None
        else:
            self.model = "gemini-2.5-flash"

    def generate_lighting_script(self, events, fixtures_info):
        """
        Invia gli eventi MIDI a Gemini per generare uno script luci completo
        sotto forma di array JSON compatibile con il nostro mapper.
        """
        if not self.model:
            print("[AI-Fallback] API Key non trovata. Uso il mapping di base (Rule-based).")
            return None
        
        print("🤖 [AI-Analyzer] Analisi musicale in corso con Gemini API HTTP...")
        
        # Limitiamo gli eventi se sono troppi per evitare prompt enormi
        sample_events = events[:100] 
        
        prompt = f"""
        Sei un Light Jockey professionista. Il tuo compito è generare uno show di luci sincronizzato.
        Qui c'è una lista di eventi MIDI in ordine cronologico.
        Eventi:
        {json.dumps(sample_events, indent=2)}

        Le fixture disponibili nel rig sono:
        {json.dumps(fixtures_info, indent=2)}

        Regole:
        1. Analizza il ritmo, l'altezza (pitch) e l'energia (velocity).
        2. Le note basse e calde potrebbero usare i PAR. I climax o suoni alti potrebbero usare strobo.
        3. Associa ad ogni l'evento MIDI una fixture.
        
        Restituisci ESCLUSIVAMENTE un array JSON (nessun altro testo, niente markdown).
        L'array deve contenere un oggetto per ogni evento ricevuto in ingresso. 
        Formato richiesto di un oggetto di output:
        {{
            "t": <stesso tempo t dell'evento>,
            "target": "par" | "moving_head" | "strobe",
            "id": "<id di una fixture disponibile>",
            "color": [<R 0-255>, <G 0-255>, <B 0-255>],
            "intensity": <intensità 0-255 derivata da velocity o logica tua>,
            "pan": <0-255 - solo per moving_head>,
            "tilt": <0-255 - solo per moving_head>,
            "rate": <0-255 - solo per strobe>
        }}
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2
            }
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            result_text = data["candidates"][0]["content"]["parts"][0]["text"]
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            
            script_luci = json.loads(result_text)
            print("✨ [AI-Analyzer] Analisi completata! Script luci generato.")
            return script_luci
        except Exception as e:
            print(f"❌ [AI-Error] Errore durante l'analisi HTTP: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                print("Dettagli API:", response.text)
            return None
