from dotenv import load_dotenv
from agents import Agent ,Runner,trace

import asyncio

load_dotenv()

agent = Agent(name='Joker',instructions="You are a joker and you are funny don't repeat the same joke",model='gpt-4o-mini' )

result = asyncio.run(Runner.run(agent, 'Tell me a joke'))
print(result.final_output)
    