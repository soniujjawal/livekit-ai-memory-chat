import os,openai,asyncio
from livekit import agents
from livekit.agents import AutoSubscribe
from dotenv import load_dotenv
import httpx

load_dotenv()
openai.api_key=os.getenv("OPENAI_API_KEY")

async def main():
    async with agents.Room.connect(os.getenv("LIVEKIT_URL"),os.getenv("LIVEKIT_API_KEY"),os.getenv("LIVEKIT_API_SECRET"),auto_subscribe=AutoSubscribe.CHAT) as room:
        async for e in room:
            if isinstance(e,agents.ChatReceived):
                u=e.message.sender.identity
                m=e.message.message
                async with httpx.AsyncClient() as c:
                    mem=await c.post("https://api.mem0.ai/retrieve",json={"user":u,"query":m},headers={"Authorization":"Bearer "+os.getenv("MEM0_API_KEY")})
                r=openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role":"system","content":str(mem.json())},{"role":"user","content":m}])
                await room.local_participant.publish_chat_message(r["choices"][0]["message"]["content"])
asyncio.run(main())
