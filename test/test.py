import asyncio

def hello_world(loop):
    print('Hello World')
    loop.stop()


loop = asyncio.get_event_loop()
# Schedule a call to hello_world()
loop.run_until_complete(hello_world, loop)
loop.run_forever()
