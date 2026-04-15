import os
import json
import requests
import subprocess
from dotenv import load_dotenv

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2") 
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api")
        self.check_and_pull_model()

    def check_and_pull_model(self):
        """Check if the model is present locally, otherwise pull it via CLI so the user sees progress."""
        try:
            print(f"[STATUS] Checking availability of model {self.model} on Ollama...")
            response = requests.get(f"{self.ollama_url}/tags", timeout=5)
            response.raise_for_status()
            models = [m.get("name") for m in response.json().get("models", [])]
            
            if self.model not in models and f"{self.model}:latest" not in models:
                print(f"[WARNING] Model {self.model} not found. Starting download (this might take a while)...")
                subprocess.run(["ollama", "pull", self.model], check=True)
                print("[SUCCESS] Download completed successfully!")
            else:
                print(f"[SUCCESS] Model {self.model} is already present.")
        except requests.exceptions.ConnectionError:
            print("[ERROR] Cannot connect to Ollama to check models. Ensure it is running.")
        except Exception as e:
            print(f"[ERROR] Error during model check: {e}")

    def generate_lighting_script(self, events, fixtures_info):
        """
        Send MIDI events to a local model via Ollama to generate a lighting script.
        The returned array is a JSON compatible with our mapper.
        """
        print(f"[AI-Analyzer] Generating complete show (model: {self.model})...")
                
        prompt = f"""
        You are a professional software. Generate a lighting show orchestrated on the provided rhythms.
        MIDI Events:
        {json.dumps(events, indent=2)}

        Available Fixtures:
        {json.dumps(fixtures_info, indent=2)}

        Associate each event with a fixture or a group of them based on energy to create a show. 
        Use ONLY and EXCLUSIVELY the exact IDs specified in the "id" field of the available Fixtures (write them as numeric strings, e.g. "1", "4", "31"). DO NOT invent IDs like "par_1".
        
        Return EXCLUSIVELY a JSON array, no other text. 
        YOU MUST ABSOLUTELY return a LARGE LIST containing ONE JSON OBJECT for EVERY SINGLE EVENT.
        Exact required format (use these square brackets!):
        [
          {{
              "t": <event time t>,
              "target": "rgb_par" | "moving_head" | "led_bar",
              "id": "<exact numerical id of the fixture>",
              "color": [<R>, <G>, <B>],
              "intensity": <intensity 0-255>,
              "pan": <0-255 (only for moving_head)>,
              "tilt": <0-255 (only for moving_head)>
          }}
        ]
        """

        return self._call_ollama(prompt)

    def refine_script_with_chat(self, events, chat_message, fixtures_info):
        """
        Regenerate the script incorporating the user directive, 
        avoiding passing the old script to prevent Context Window overflow of micro models.
        """
        print(f"[AI-Chat] Guided regeneration: '{chat_message}'...")

        prompt = f"""
        You are a professional lighting designer.
        MANDATORY USER DIRECTIVE FOR THE SHOW: "{chat_message}"
        (Example: if asked "all blue", set [0,0,255]. If asked "all dark" or "off", set intensity: 0. Ignore creativity and respect the command strictly).
        
        MIDI Events:
        {json.dumps(events, indent=2)}

        Fixtures:
        {json.dumps(fixtures_info, indent=2)}

        Return EXCLUSIVELY a JSON array. 
        YOU MUST ABSOLUTELY return a LARGE LIST containing ONE JSON OBJECT for EVERY SINGLE EVENT.
        Exact required format (use these square brackets!):
        [
          {{
              "t": <event time t>,
              "target": "rgb_par" | "moving_head" | "led_bar",
              "id": "<exact numerical id of the fixture>",
              "color": [<R>, <G>, <B>],
              "intensity": <intensity 0-255>,
              "pan": <0-255 (only for moving_head)>,
              "tilt": <0-255 (only for moving_head)>
          }}
        ]
        """
        
        return self._call_ollama(prompt)
        
    def _call_ollama(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        
        try:
            response = requests.post(f"{self.ollama_url}/generate", json=payload, timeout=600)
            response.raise_for_status()
            data = response.json()
            
            result_text = data.get("response", "").strip()
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(result_text)
        except Exception as e:
            print(f"[AI-Error] Error: {e}")
            return None
