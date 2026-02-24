import asyncio
import logging
import time
from dotenv import load_dotenv

# Core SDK and Plugins
from livekit.agents import JobContext, WorkerOptions, cli, AgentSession, Agent
from livekit.plugins import google, silero, deepgram, cartesia

load_dotenv()
logger = logging.getLogger("voice-agent")

async def entrypoint(ctx: JobContext):
    # 2026 UPGRADE: Using gemini-2.0-flash to avoid 404/Retirement errors
    session = AgentSession(
        stt=deepgram.STT(),
        llm=google.LLM(model="gemini-2.0-flash"), 
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
    )

    agent = Agent(
        instructions="You are a helpful, brief voice AI. Answer concisely.",
    )

    last_interaction = time.time()

    @session.on("user_started_speaking")
    def _on_user_speech():
        nonlocal last_interaction
        last_interaction = time.time()

    # Silence Handling: 20s Reminder
    async def monitor_silence():
        nonlocal last_interaction
        while True:
            await asyncio.sleep(5)
            if time.time() - last_interaction >= 20:
                # Use generate_reply for proactive follow-up
                await session.generate_reply(instructions="Friendly reminder that you are still here.")
                last_interaction = time.time()

    await ctx.connect()
    
    # Start the session
    await session.start(agent=agent, room=ctx.room)
    
    # Run the silence monitor in the background
    asyncio.create_task(monitor_silence())
    
    # Initial greeting to confirm connection
    await session.generate_reply(instructions="Greet the user and say 'I am connected and ready.'")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))