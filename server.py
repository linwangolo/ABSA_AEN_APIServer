# -*- coding: utf-8 -*-

import time
import sys
import opinion_aen
import asyncio
from aiohttp import web
import json

sem = asyncio.Semaphore(1000)

async def opinion_predict(target, context):
    inputs = opinion_aen.Input(target, context).data
    results = []
    for inp in inputs:
        results.append(opinion_aen.predict(inp))
    return results


async def predict(request):
    async with sem:
        data = await request.json()
        data['t2'] = time.time()
        results = await opinion_predict(data['target'], data['context'])
        data['results'] = results
        data['t3'] = time.time()
        resp = web.Response(body=json.dumps(data, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
        resp.content_type = 'application/json;charset=utf-8'
        return resp



if __name__ == '__main__':

    # init web application
    app = web.Application()

    # setting routes
    app.add_routes([web.post('/predict', predict)])

    # start web application
    web.run_app(app, port=1600)

