# -*- coding: utf-8 -*-

import time
import sys
sys.path.insert(0,'../')
import opinion_aen
import asyncio
from aiohttp import web
import json
import logging
stdio_handler = logging.StreamHandler()
stdio_handler.setLevel(logging.INFO)
_logger = logging.getLogger('aiohttp.server')
_logger.addHandler(stdio_handler)
_logger.setLevel(logging.DEBUG)

sem = asyncio.Semaphore(1000)

async def opinion_predict(data, batch_size):
    opinion_aen.opt.batch_size = batch_size
    inputs = opinion_aen.Input(data).data
    prob, polar = opinion_aen.predict(inputs)
    return prob, polar


async def predict(request):
    async with sem:
        data = await request.json()
        data['t2'] = time.time()
        prob, polar = await opinion_predict(data['data'], data['batch_size'])
        data['prob'] = prob[0].tolist()
        data['polar'] = polar[0]
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

