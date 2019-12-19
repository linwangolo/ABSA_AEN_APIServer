# -*- coding: utf-8 -*-
# file: __init__.py
# author: songyouwei <youwei0314@gmail.com>
# Copyright (C) 2018. All Rights Reserved.

import time
import sys
sys.path.insert(0,'../')
import opinion_aen
import asyncio
from aiohttp import web

sem = asyncio.Semaphore(1)

async def opinion_predict(target, context):
    inputs = opinion_aen.Input(target, context)
    print(inputs)
    results = opinion_aen.predict(inputs.data)
    return results

async def predict(request):
    async with sem:
        data = await request.json()
        data['t2'] = time.time()
        results = await opinion_predict(data['target'], data['context'])
        data['results'] = results
        data['t3'] = time.time()
        return web.json_response(data)



if __name__ == '__main__':

    # init web application
    app = web.Application()

    # setting routes
    app.add_routes([web.post('/predict', predict)])

    # start web application
    web.run_app(app, port=1600)

