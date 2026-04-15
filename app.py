import streamlit as st
import os
import pygame
import time

from src.midi_parser import MidiParser
from src.ai_analyzer import AIAnalyzer
from src.fixtures import FIXTURES
from src.artnet_sender import ArtNetSender
from src.mapping import Mapper
from src.playback import PlaybackEngine

st.set_page_config(page_title="AudioToLights AI", layout="wide", initial_sidebar_state="collapsed")

# --- CSS STYLES (SINGLE PAGE UI) ---
st.markdown("""
<style>
/* Reduce padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 95% !important;
}

/* Hide top bar and footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Bottom player bar - Glassmorphism */
.player-bar-container {
    background: rgba(15, 17, 26, 0.85);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    padding: 15px 25px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    margin-top: 10px;
}

/* Prevent global scrolling for wide layouts, enforcing container max-heights */
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "events" not in st.session_state: st.session_state.events = []
if "script" not in st.session_state: st.session_state.script = []
if "audio_path" not in st.session_state: st.session_state.audio_path = ""
if "midi_path" not in st.session_state: st.session_state.midi_path = ""
if "is_playing" not in st.session_state: st.session_state.is_playing = False
if "analyzer" not in st.session_state:
    with st.spinner("Initializing AI Lighting Analysis..."):
        st.session_state.analyzer = AIAnalyzer()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hello! Use this chat to refine your lighting script!"}]

# Stop helper function
def force_stop_audio():
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.unload()
            except AttributeError:
                pass # for older pygame versions
            pygame.mixer.quit() # Force release of the audio file on Windows
    except: pass
    st.session_state.is_playing = False

# Check if a rerun happened and stop music playback
if not st.session_state.is_playing:
    force_stop_audio()


# --- HEADER & SETUP ---
col_logo, col_chat = st.columns([8, 2])
with col_logo:
    st.title("AudioToLights - Control Board")
with col_chat:
    with st.popover("Open AI Assistant", use_container_width=True):
        st.markdown("**AI Show Editor**")
        chat_container = st.container(height=300)
        for msg in st.session_state.chat_history:
            chat_container.chat_message(msg["role"]).write(msg["content"])
            
        prompt = st.chat_input("Example: Make all PARs blue...")
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            chat_container.chat_message("user").write(prompt)
            if len(st.session_state.script) == 0:
                st.session_state.chat_history.append({"role": "assistant", "content": "Generate the base script first."})
                st.rerun()
            else:
                with chat_container.chat_message("assistant"):
                    with st.spinner("Rewriting sequence..."):
                        updated = st.session_state.analyzer.refine_script_with_chat(st.session_state.events, prompt, FIXTURES)
                        if updated:
                            st.session_state.script = updated
                            st.session_state.chat_history.append({"role": "assistant", "content": "Modifications applied!"})
                        else:
                            st.session_state.chat_history.append({"role": "assistant", "content": "Update error."})
                st.rerun()

# --- MAIN WORKSPACE ---
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    config_container = st.container(height=400)
    with config_container:
        st.subheader("1. Input Loading")
        audio_file = st.file_uploader("Audio Track (MP3/WAV)", type=["mp3", "wav"])
        midi_file = st.file_uploader("MIDI Track (.mid)", type=["mid", "midi"])
        
        if st.button("Extract MIDI Timeline", type="primary", use_container_width=True):
            if audio_file and midi_file:
                os.makedirs("data", exist_ok=True)
                audio_path = os.path.join("data", audio_file.name)
                midi_path = os.path.join("data", midi_file.name)
                
                try:
                    with open(audio_path, "wb") as f: f.write(audio_file.getbuffer())
                except PermissionError:
                    pass # Prevent crash, correct file is already in memory
                    
                try:
                    with open(midi_path, "wb") as f: f.write(midi_file.getbuffer())
                except PermissionError:
                    pass
                st.session_state.audio_path, st.session_state.midi_path = audio_path, midi_path
                
                parser = MidiParser(midi_path)
                st.session_state.events = parser.parse()
                st.success(f"Timeline extracted. {len(st.session_state.events)} rhythmic notes found!")
            else:
                st.error("PLEASE UPLOAD BOTH FILES!")

        st.markdown("---")
        st.subheader("2. AI Scenography")
        disabled_gen = len(st.session_state.events) == 0
        if st.button("Generate Colors and Dynamics", use_container_width=True, disabled=disabled_gen):
            with st.spinner("Analyzing rhythmic variations with AI..."):
                script = st.session_state.analyzer.generate_lighting_script(st.session_state.events, FIXTURES)
                if script:
                    st.session_state.script = script
                    st.success("Scenographic Script Generated!")
                else:
                    st.error("AI Failure.")

with col_right:
    timeline_container = st.container(height=400)
    with timeline_container:
        st.subheader(f"Progress Timeline ({len(st.session_state.events)} Events)")
        if not st.session_state.script:
            st.info("No timeline preset. Load files and start AI.")
        else:
            with st.expander("JSON Base Dictionary Preview", expanded=False):
                st.json(st.session_state.script)
            
            # Preview events passing in real-time during playback
            event_live_box = st.empty()
            event_live_box.success("System Armed and Ready.")


# --- PHYSICAL MP3 PLAYER & LIVE PLAYBACK ---
st.markdown('<div class="player-bar-container">', unsafe_allow_html=True)
pl_col1, pl_col2, pl_col3 = st.columns([1, 6, 1])

with pl_col1:
    if st.button("STOP", use_container_width=True):
        force_stop_audio()
        st.rerun()

with pl_col2:
    # Static player UI render
    player_ui = st.empty()
    player_pb = st.empty()
    player_pb.progress(0, text="00:00 / 00:00 - STANDBY")

with pl_col3:
    play_btn_disabled = not st.session_state.script or not st.session_state.events or st.session_state.is_playing
    if st.button("LIVE PLAY", type="primary", use_container_width=True, disabled=play_btn_disabled):
        # --- PLAYBACK LOOP (MAIN THREAD) ---
        st.session_state.is_playing = True
        sender = ArtNetSender(ip="127.0.0.1", port=6454)
        mapper = Mapper(ai_script=st.session_state.script, fixtures=FIXTURES)
        playback = PlaybackEngine(sender, mapper, fixtures_list=FIXTURES)
        
        events = st.session_state.events
        audio_path = st.session_state.audio_path
        
        total_duration = max([e["t"] for e in events]) + 2.0 if events else 1.0
        
        # Audio Initialization
        try:
            pygame.mixer.init()
            if os.path.exists(audio_path):
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
        except Exception as e:
            st.error("Audio Load Error: "+ str(e))
        
        player_ui.markdown("<h4 style='text-align: center; color: #00ff88; margin: 0;'>PLAYING THEATRE SEQUENCE</h4>", unsafe_allow_html=True)
        
        start_time = time.time()
        
        # Loop Events
        for idx, event in enumerate(events):
            target_t = event["t"]
            
            while True:
                now = time.time()
                elapsed = now - start_time
                time_left = target_t - elapsed
                
                # Visual Update Routine (throttle to ~15 fps to prevent Streamlit flickering)
                pct = min(elapsed / total_duration, 1.0)
                txt = f"{int(elapsed//60):02d}:{int(elapsed%60):02d} / {int(total_duration//60):02d}:{int(total_duration%60):02d}"
                player_pb.progress(pct, text=txt)
                
                if time_left > 0:
                    time.sleep(max(min(time_left, 0.05), 0.001))
                else: break
            
            # FIRE OSC
            actions = mapper.process_event(event)
            playback.dispatch_actions(actions)
            
            # UPDATE TIMELINE/LIVE EVENT INDICATOR
            t_type = actions[0]["target"] if actions else "Generic"
            desc = f"**CUE {idx+1}/{len(events)}** | {target_t:.2f}s | **{t_type.upper()}** (Note {event['note']})"
            event_live_box.warning(desc)
            
        # Post Loop Cleanup
        force_stop_audio()
        player_ui.markdown("<h4 style='text-align: center; color: white; margin: 0;'>PLAYBACK FINISHED</h4>", unsafe_allow_html=True)
        player_pb.progress(1.0, text="End of sequence")
        time.sleep(1)
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
