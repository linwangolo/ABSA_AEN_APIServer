import aiohttp
import asyncio


async def make_post(session, data):
    url = 'http://10.60.10.128:1000/predict'
    print(f'making post to {url}')
    print(data)
    async with session.post(url, data=data) as resp:
        print(await resp.text())


async def main():
#    data_ls = ['{"target":"他", "context":"他是个讨厌鬼 但他是好人"}', '{"target":"他", "context":"他是个讨厌鬼 但他是好人"}', 
#                '{"target":"他", "context":"他是个讨厌鬼 但他是好人"}', '{"target":"他", "context":"他是个讨厌鬼 但他是好人"}',
#                '{"target":"他", "context":"他是个讨厌鬼 但他是好人"}','{"target":"他", "context":"他是个讨厌鬼 但他是好人"}']
    data_ls = ['{"target":"他", "context":"他是个讨厌鬼 但他是好人"}']
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
                *[make_post(session, data = data) for data in data_ls]
        )

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
