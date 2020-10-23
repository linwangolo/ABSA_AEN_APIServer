# -*- coding: utf-8 -*-

import argparse
import time
import sys
import opinion_aen
import asyncio
from aiohttp import web
import json
from data_utils import cut_sentence, find_target
import logging
stdio_handler = logging.StreamHandler()
stdio_handler.setLevel(logging.INFO)
_logger = logging.getLogger('aiohttp.server')
_logger.addHandler(stdio_handler)
_logger.setLevel(logging.DEBUG)



async def opinion_predict(data, batch_size):
    model.opt.batch_size = batch_size
    inputs = opinion_aen.Input(data).data
    prob, polar = model.predict(inputs)
    return prob, polar


async def predict(request):
    async with sem:
        data = await request.json()
        data['t2'] = time.time()
        cut_data = cut_sentence(data['data'], 15)
        data_pair = find_target(cut_data, data['query'])
        prob, polar = await opinion_predict(data_pair, data['batch_size'])
        tmp_prob = [item.tolist() for p_ls in prob for item in p_ls]
        tmp_polar = [item for sublist in polar for item in sublist]
        art_index = [i['art_index'] for i in data_pair]
        art_set = set(art_index)
        data['polar'] = []
        data['prob'] = []
        for ind in art_set:
            indices = [i for i, x in enumerate(art_index) if x == ind]
            data['polar'].append([tmp_polar[i] for i in indices])
            data['prob'].append([tmp_prob[i] for i in indices])
        data['t3'] = time.time()
        resp = web.Response(body=json.dumps(data, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
        resp.content_type = 'application/json;charset=utf-8'
        return resp



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default = 1600, type=int)
    parser.add_argument('--model_path', default = '~/opinion_aen/state_dict/aen_bert_CCF_val_acc0.9048', type=str)
    parser.add_argument('--thread_num', default = 1000, type=int)
    arg = parser.parse_args()

    sem = asyncio.Semaphore(arg.thread_num) # 1000
    model_path = arg.model_path 
    model = opinion_aen.model(model_path)

    # init web application
    app = web.Application()

    # setting routes
    app.add_routes([web.post('/predict', predict)])

    # start web application
    web.run_app(app, port=arg.port) # 1600

