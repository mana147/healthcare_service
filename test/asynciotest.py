import asyncio


async def cor_1():
    print('cor_1')
    await asyncio.sleep(1000)

async def cor_2():
    print('cor_2')
    await asyncio.sleep(2000)

loop = asyncio.get_event_loop()
loop.run_until_complete( asyncio.gather( cor_1() , cor_2() ) )
