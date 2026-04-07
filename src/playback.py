import time

class PlaybackEngine:
    def __init__(self, osc_sender, mapper):
        self.sender = osc_sender
        self.mapper = mapper
        
    def play(self, events):
        """
        Takes a list of chronological events with absolute times ("t") in seconds.
        Sleeps between events and dispatches them to the mapper and then OSC.
        """
        if not events:
            print("No events to play.")
            return
            
        start_time = time.time()
        
        for event in events:
            # Calculate how long to wait until the next event
            target_time = start_time + event["t"]
            now = time.time()
            sleep_duration = target_time - now
            
            if sleep_duration > 0:
                time.sleep(sleep_duration)
                
            # Now it's time to process the event
            actions = self.mapper.process_event(event)
            self.dispatch_actions(actions)
            
    def dispatch_actions(self, actions):
        for action in actions:
            target = action.get("target")
            fixture_id = action.get("id")
            
            if target == "par":
                self.sender.send_color(fixture_id, *action["color"])
                self.sender.send_intensity(fixture_id, action["intensity"])
            elif target == "moving_head":
                self.sender.send_color(fixture_id, *action["color"])
                self.sender.send_pan_tilt(fixture_id, action["pan"], action["tilt"])
                self.sender.send_intensity(fixture_id, action["intensity"])
            elif target == "strobe":
                self.sender.send_strobe_rate(fixture_id, action["rate"])
                self.sender.send_intensity(fixture_id, action["intensity"])
                
            # Log action briefly
            print(f"[{time.time():.2f}] Action dispatched -> {fixture_id} | Type: {target}")
