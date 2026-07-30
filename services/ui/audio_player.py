import base64
import streamlit as st


def render_persistent_audio_player(audio_bytes: bytes, audio_id: str):
    """
    Renders a persistent HTML5 background audio player attached to the browser's top window context.
    Prevents Streamlit reruns from stopping audio mid-sentence and uses non-deprecated st.html API.
    """
    if not audio_bytes or not audio_id:
        return

    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    html_code = f"""
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
    if hasattr(st, "html"):
        st.html(html_code)
    else:
        st.components.v1.html(html_code, height=0, width=0)
