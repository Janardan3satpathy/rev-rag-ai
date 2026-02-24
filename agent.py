import asyncio
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_pipeline import VoicePipelineAgent
from livekit.plugins import openai, silero, deepgram, cartesia

load_dotenv()
logger = logging.getLogger("voice-agent")

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text="You are a helpful voice assistant. Keep your responses concise.",
    )

    # Initialize the Agent with high-performance plugins
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(),
        tts=cartesia.TTS(),
        chat_ctx=initial_ctx,
        # A. NO OVERLAP: 
        # This setting ensures the agent cuts off immediately when user speech is detected.
        interrupt_speech_duration=0.4, 
    )

    # State tracking for silence handling
    last_interaction_time = datetime.now()

    @agent.on("user_started_speaking")
    def _user_started():
        nonlocal last_interaction_time
        last_interaction_time = datetime.now()

    # B. SILENCE HANDLING:
    # A background task that checks for inactivity
    async def silence_monitor():
        nonlocal last_interaction_time
        while True:
            await asyncio.sleep(5)
            idle_time = (datetime.now() - last_interaction_time).total_seconds()
            
            if idle_time >= 20:
                # Play a short reminder and reset the timer
                await agent.say("I'm still here if you need anything!", allow_interruptions=True)
                last_interaction_time = datetime.now()

    await ctx.connect()
    agent.start(ctx.room)
    
    # Start the silence watcher
    asyncio.create_task(silence_monitor())
    
    # Initial greeting
    await agent.say("Hello! I am joined and listening.", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
