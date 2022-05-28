# achain

An asynchronous way to chain together multiple asynchronous generators.

Whilst this is supported by `asychio.Queue`, in practice it's quite unintuitive getting this to work how you want.

`achain` sorts this out for you:

```
import asyncio

from achain import achain

async def sleeper(time):
    for i in range(3):
        await asyncio.sleep(time)
        yield time


async def main():
    async for out in achain(sleeper(0.4), sleeper(1)):
        print(out)

asyncio.run(main())

# output:
0.4
0.4
1
0.4
1
1
```

It's not completely clear to me how safe this is if things go wrong.

With a bit of extra work, we can extend the class behind the `achain`, to make `DynChain`.

This adds the functionality that new generators can be added during iteration e.g.

```
from achain import DynChain

async def main():
    chain = DynChain(sleeper(0.4), sleeper(1))
    
    
    i = 0
    async for out in chain:
        print(out)
        i += 1

        if i == 2:
            async def surprise():
                yield 'surprise'

            chain.add_generator(surprise())

asyncio.run(main())
# outputs

0.4
0.4
surprise
1
0.4
1
1
```

## Implementation Detail

Something to note is that because of the way this works, unlike iterating through regular generators - where the result is generated on demand,
technically here the next result is anychronously generated, queued, then retreived, allowing the next result to asynchronously be queued. 

Hence it's kinda on demand, but always 1 step ahead!