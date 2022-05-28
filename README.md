# achain

An asynchronous way to chain together multiple asynchronous generators.

Whilst this is supported by `asychio.Queue`, in practice it's quite unintuitive getting this to work how you want.

`achain` sorts this out for you:

```
import asychio

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

This should handle things going wrong a bit better and adds the functionality that new generators can be added during iteration e.g.

```
async def main():
    chain = DynChain(sleeper(0.4), sleeper(1))
    
    with chain:
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

wrapping in the with block is a bit ugly, but does ensure things are cleaned up properly should things go wrong.

	
