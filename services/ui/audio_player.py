import base64
import streamlit.components.v1 as components


def render_persistent_audio_player(audio_bytes: bytes, audio_id: str):
    """
    Renders a persistent HTML5 background audio player attached to the browser's top window context.
    Prevents Streamlit reruns or st_autorefresh from stopping audio mid-sentence.
    """
    if not audio_bytes or not audio_id:
        return

    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    js_code = f"""
    <script>
        (function() {{
            try {{
                const audioData = "data:audio/mp3;base64,{b64_audio}";
                const targetWin = window.parent || window;
                if (!targetWin._gym_audio_player) {{
                    targetWin._gym_audio_player = new Audio();
                }}
                const player = targetWin._gym_audio_player;
                if (targetWin._last_audio_id !== "{audio_id}") {{
                    targetWin._last_audio_id = "{audio_id}";
                    player.src = audioData;
                    player.play().catch(function(e) {{
                        console.log("Browser audio playback warning:", e);
                    }});
                }}
            }} catch (err) {{
                console.error("Audio player JS error:", err);
            }}
        }})();
    </script>
    """
    components.html(js_code, height=0, width=0)
