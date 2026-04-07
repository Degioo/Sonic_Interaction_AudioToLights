import time
from src.osc_sender import OSCSender

def main():
    print("--------------------------------------------------")
    print("Modalità Mapping QLC+")
    print("Premi Ctrl+C per fermare lo script.")
    print("--------------------------------------------------")
    
    # --- CAMBIA QUESTO NOME PER MAPPARE LE ALTRE LUCI ---
    # Sostituisci "par_1" con "par_2", "mh_1", "mh_2", o "strobe_1"
    TARGET_FIXTURE = "strobe_1"
    # ----------------------------------------------------

    sender = OSCSender(ip="127.0.0.1", port=7700)
    
    try:
        while True:
            sender.send_intensity(TARGET_FIXTURE, 255)
            print(f"Inviato valore 255 a /{TARGET_FIXTURE}/intensity - Clicca su Rilevamento Automatico ora!")
            time.sleep(1)
            
            sender.send_intensity(TARGET_FIXTURE, 0)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nMapping terminato.")

if __name__ == "__main__":
    main()
