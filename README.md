Setup Instructions
Clone the repository: git clone <repo-url>

Install dependencies: ```bash
pip install livekit-agents livekit-plugins-openai livekit-plugins-silero livekit-plugins-deepgram livekit-plugins-cartesia python-dotenv

Environment Variables: Create a .env file with:

LIVEKIT_URL: Your LiveKit project URL.

LIVEKIT_API_KEY / LIVEKIT_API_SECRET: From your LiveKit dashboard.

DEEPGRAM_API_KEY: For STT.

CARTESIA_API_KEY: For ultra-low latency TTS.

OPENAI_API_KEY: For the brain (LLM).

How to Run
Run the agent in "dev" mode to connect to your cloud or local LiveKit instance:

Bash
python agent.py dev
How "No Overlap" Works
The agent utilizes Silero VAD (Voice Activity Detection) running on the agent's side. When the VAD detects incoming audio frames that match a human speech pattern, the VoicePipelineAgent immediately issues a "cancel" command to the TTS playout buffer. This ensures the agent stops mid-sentence the moment you speak.

Limitations
Network Latency: If the user has a high-ping connection, the "stop" signal might arrive after a slight delay.

Ambient Noise: High background noise can occasionally trick the VAD into thinking the user is speaking.
