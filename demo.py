import random
import asyncio

from achain import achain, DynChain


async def sleeper(time):
	for i in range(3):
		await asyncio.sleep(time)
		yield time


async def demo1():
    async for out in achain(sleeper(0.4), sleeper(1)):
        print(out)

        
async def demo2(): 
    chain = DynChain(sleeper(0.4), sleeper(1))
    
    i = 0
    async for out in chain:
        print(out)
        i += 1
        if i == 2:
            async def surprise():
                yield 'surprise'
            
            chain.add_generator(surprise())  # new generators can be added during iteration!


if __name__ == '__main__':
    asyncio.run(demo1())
    asyncio.run(demo2())