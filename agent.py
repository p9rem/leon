import ctypes, sys
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, google
import platform

from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import (
    get_weather, manage_notes, manage_todo,
    control_os, get_system_status, get_current_time,launch_application,send_whatsapp_message,execute_task
)

load_dotenv()

def ensure_admin():
    if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,
            " ".join([f'"{arg}"' for arg in sys.argv]), None, 1)
        sys.exit()

ensure_admin()

class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(voice="Aoede", temperature=0.7),
            tools=[get_weather, manage_notes, manage_todo, control_os, get_system_status, get_current_time,launch_application,send_whatsapp_message,execute_task]
        )

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession()
    await session.start(
        room=ctx.room, agent=Assistant(),
        room_input_options=RoomInputOptions(video_enabled=False,
        noise_cancellation=noise_cancellation.BVC())
    )
    await ctx.connect()
    await session.generate_reply(instructions=SESSION_INSTRUCTION)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
