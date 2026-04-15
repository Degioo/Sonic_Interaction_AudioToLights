import time

class PlaybackEngine:
    def __init__(self, sender, mapper, fixtures_list):
        self.sender = sender
        self.mapper = mapper
        self.fixtures_dict = {str(f["id"]): f for f in fixtures_list}
        
    def play(self, events, callback=None):
        """
        Takes a list of chronological events with absolute times ("t") in seconds.
        Sleeps between events and dispatches them to the mapper and then OSC.
        If callback is provided, it is called to update progress. It returns False to stop.
        """
        if not events:
            print("No events to play.")
            return
            
        start_time = time.time()
        # Find the max time of all events to send total duration
        total_duration = max([e["t"] for e in events]) if events else 0
        
        for idx, event in enumerate(events):
            target_time = start_time + event["t"]
            
            while True:
                now = time.time()
                sleep_duration = target_time - now
                
                if callback:
                    should_continue = callback({
                        "action": "progress",
                        "current_time": now - start_time,
                        "total_duration": total_duration,
                        "current_event_index": idx
                    })
                    if not should_continue:
                        return # Stop playback

                if sleep_duration > 0:
                    # Insert a simple frame-by-frame fade decay
                    for ch in range(512):
                        val = self.sender.dmx_data[ch]
                        if val > 0:
                            self.sender.dmx_data[ch] = max(0, val - 10)
                    self.sender.send_universe()
                    
                    time.sleep(min(sleep_duration, 0.05))
                else:
                    break
                
            # Now it's time to process the event
            actions = self.mapper.process_event(event)
            self.dispatch_actions(actions)
            
            if callback:
                should_continue = callback({
                    "action": "event_trigger",
                    "current_time": time.time() - start_time,
                    "event": event,
                    "current_event_index": idx
                })
                if not should_continue:
                    return # Stop playback

            
    def dispatch_actions(self, actions):
        for action in actions:
            target = action.get("target")
            fixture_id = str(action.get("id"))
            
            fixt = self.fixtures_dict.get(fixture_id)
            if not fixt: continue
            
            addr = fixt["address"]
            dim = action.get("intensity", 255)
            
            if target in ["par", "rgb_par"]:
                r, g, b = action.get("color", (255,255,255))
                channels_count = fixt.get("channels", 0)
                
                if channels_count == 8:
                    # Starville RGBWA UV (1=Dim, 2=R, 3=G, 4=B, 5=W, 6=A, 7=UV, 8=Str)
                    self.sender.set_channel(addr + 0, dim)
                    self.sender.set_channel(addr + 1, r)
                    self.sender.set_channel(addr + 2, g)
                    self.sender.set_channel(addr + 3, b)
                elif channels_count == 6:
                    # Showtec RGBWA UV (1=R, 2=G, 3=B, 4=W, 5=A, 6=UV) -> simulated dimmer
                    self.sender.set_channel(addr + 0, int(r * (dim/255.0)))
                    self.sender.set_channel(addr + 1, int(g * (dim/255.0)))
                    self.sender.set_channel(addr + 2, int(b * (dim/255.0)))
                elif channels_count == 9:
                    # Varitec RGBW (assuming 1=Dim, 2=R, 3=G, 4=B, 5=W)
                    self.sender.set_channel(addr + 0, dim)
                    self.sender.set_channel(addr + 1, r)
                    self.sender.set_channel(addr + 2, g)
                    self.sender.set_channel(addr + 3, b)
                elif channels_count == 3:
                    # Fresnel (1=R, 2=G, 3=B or 1=Dim)
                    self.sender.set_channel(addr + 0, int(r * (dim/255.0)))
                    self.sender.set_channel(addr + 1, int(g * (dim/255.0)))
                    self.sender.set_channel(addr + 2, int(b * (dim/255.0)))
                else:
                    self.sender.set_channel(addr + 0, r)
                    self.sender.set_channel(addr + 1, g)
                    self.sender.set_channel(addr + 2, b)
                    self.sender.set_channel(addr + 3, dim)
                
            elif target == "moving_head":
                r, g, b = action.get("color", (255,255,255))
                pan = action.get("pan", 127)
                tilt = action.get("tilt", 127)
                channels_count = fixt.get("channels", 0)
                
                if channels_count == 14:
                    # Starville MH110WS (1=Pan, 3=Tilt, 6=Dimmer, 8=R, 9=G, 10=B)
                    self.sender.set_channel(addr + 0, pan)
                    self.sender.set_channel(addr + 2, tilt)
                    self.sender.set_channel(addr + 5, dim)
                    self.sender.set_channel(addr + 7, r)
                    self.sender.set_channel(addr + 8, g)
                    self.sender.set_channel(addr + 9, b)
                elif channels_count == 16:
                    # ATOMIC BEAM 7R (1=ColorWheel, 3=Dimmer, 10=Pan, 12=Tilt)
                    color_wheel_idx = 0
                    if r > 100 and g < 50 and b < 50: color_wheel_idx = 10 # Reddish
                    elif b > 100 and r < 50: color_wheel_idx = 30 # Blueish
                    elif g > 100 and r < 50: color_wheel_idx = 60 # Greenish
                    
                    self.sender.set_channel(addr + 0, color_wheel_idx)
                    self.sender.set_channel(addr + 2, dim) # Dimmer
                    self.sender.set_channel(addr + 9, pan) # Pan (ch 10)
                    self.sender.set_channel(addr + 11, tilt) # Tilt (ch 12)
                else:
                    self.sender.set_channel(addr + 0, pan)
                    self.sender.set_channel(addr + 2, r)
                    self.sender.set_channel(addr + 3, dim)

            elif target == "led_bar":
                r, g, b = action.get("color", (255,255,255))
                channels_count = fixt.get("channels", 0)
                if channels_count == 18:
                    # 6 segments of 3 channels = 18 ch
                    for seg in range(6):
                        self.sender.set_channel(addr + (seg*3) + 0, int(r * (dim/255.0)))
                        self.sender.set_channel(addr + (seg*3) + 1, int(g * (dim/255.0)))
                        self.sender.set_channel(addr + (seg*3) + 2, int(b * (dim/255.0)))
                else:
                    self.sender.set_channel(addr + 0, r)
                    self.sender.set_channel(addr + 1, g)
                    self.sender.set_channel(addr + 2, b)
                    
            print(f"[{time.time():.2f}] Art-Net DMX {addr} -> {fixture_id} | Type: {target}")

        self.sender.send_universe()
