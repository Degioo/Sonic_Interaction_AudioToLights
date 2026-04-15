import xml.etree.ElementTree as ET
import os

FIXTURES_FILE = os.path.join(os.path.dirname(__file__), "..", "fixtures_teatro.qxfl")

def parse_qxfl():
    if not os.path.exists(FIXTURES_FILE):
        return []

    tree = ET.parse(FIXTURES_FILE)
    root = tree.getroot()
    namespace = r"{http://www.qlcplus.org/FixtureList}"
    
    fixtures = []
    
    elements = root.findall(f"{namespace}Fixture")
    if not elements:
        elements = root.findall("Fixture")
        namespace = ""

    for fixture_elem in elements:
        fid = fixture_elem.find(f"{namespace}ID")
        name = fixture_elem.find(f"{namespace}Name")
        model = fixture_elem.find(f"{namespace}Model")
        addr = fixture_elem.find(f"{namespace}Address")
        channels = fixture_elem.find(f"{namespace}Channels")
        
        if fid is not None and name is not None and model is not None:
            model_text = model.text.lower()
            
            # Determine primary target type based on keywords
            ftype = "generic"
            if "par" in model_text or "fresnel" in model_text:
                ftype = "rgb_par"
            elif "mh-110" in model_text or "7r beam" in model_text or "moving head" in model_text:
                ftype = "moving_head"
            elif "bar" in model_text:
                ftype = "led_bar"
            else:
                ftype = "rgb_par"
                
            fixtures.append({
                "id": fid.text,
                "name": name.text,
                "model_name": model.text,
                "address": int(addr.text) if addr is not None else 0,
                "channels": int(channels.text) if channels is not None else 0,
                "type": ftype
            })
            
    return fixtures

FIXTURES = parse_qxfl()
