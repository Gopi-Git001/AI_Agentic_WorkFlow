from dotenv import load_dotenv
from agents import Agent ,Runner,trace,ModelSettings

import asyncio

load_dotenv()

agent = Agent(name='Joker',instructions="You are a joker and you are funny don't repeat the same joke",model='gpt-4o-mini',model_settings=ModelSettings(temperature=1.0) )

result = asyncio.run(Runner.run(agent, "Tell me a joke don't repeat the same joke"))
print(result.final_output)
    