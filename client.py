import aiohttp
import asyncio
import pandas as pd
import json
import os
import time
import re
import math
import multiprocessing

sem = asyncio.Semaphore(100)

async def make_post(session, data):
    url = 'http://10.60.10.128:1000/predict'
    # print(f'making post to {url}')
    # print(data.decode())
    async with session.post(url, data=data) as resp:
        # try:
        output = await resp.json()
        batch_data = output['data']
        prob = output['prob']
        polar = output['polar']
        for x,y,z in zip(batch_data, prob, polar):
            result = pd.DataFrame({'prob': [y]})
            result['sentiment'] = z
            result['context'] = x['context']
            result['target'] = x['target']
            if not os.path.exists(export_path):
                result.to_csv(export_path, index = False, encoding ='utf-8-sig')
            else:
                result.to_csv(export_path, mode='a', header=False, index = False, encoding ='utf-8-sig')
        # except:
        #     pass

async def main(inputs, batch_size):
    async with sem:
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[make_post(session, data = json.dumps({'data':
                                                            [{'target':inputs.iloc[i]['word'],'context':inputs.iloc[i]['sentences']} 
                                                                                            for i in range(inputs.shape[0])], 'batch_size': batch_size}, ensure_ascii=False)) 
                ]
            )


loop = asyncio.get_event_loop()
filepath = '../2019-12-12.article_ner.csv'
df = pd.read_csv(filepath)

df = df.drop_duplicates(subset=['sentences', 'word'], keep='last')
df = df[[i in ['ORG', 'LOC', 'PER'] for i in df['type']]] 
df = df.dropna(how='any')

start_time = time.time()

def cut_sentence(arg):
    idx,row = arg
    content = row['sentences']
    # print(content)
    if pd.isnull(content):       
        return
    if len(content) <= 400:
        rows = {'word':row['word'], 'sentences': content}  
    else:
        start = 0
        idx_cut = [0]
        while True:
            if start+400 >= len(content):
                idx = len(content)
                idx_cut.append(idx)
                break
            else:
                p = ['。','!','！','?','？',' ', '.']
                idx = max([content[start:start+400].rfind(x)+start+1 for x in p])
                if idx == start:
                    p = [',','，','：',':','、',';','；','「','」','(','〈',')','〉','《','》','〈','〉','『','』']
                    idx = max([content[start:start+400].rfind(x)+start+1 for x in p])
                if idx == start:
                    idx = start+400
                idx_cut.append(idx)
                start = idx
        for k in range(1, len(idx_cut)):
            if row['end'] < idx_cut[k]:
                rows = {'word':row['word'], 'sentences': content[idx_cut[k-1]: idx_cut[k]]}
                break
    try:
        return pd.DataFrame(rows, index = [0])
    except:
        return
        
pool = multiprocessing.Pool(4)
rows_ = pool.map(cut_sentence, [(idx,row) for idx,row in df.iterrows()])
df_new = pd.concat(rows_)


df = df_new
df.index=range(df.shape[0])
rm_l = []
for i in range(df.shape[0]):
    if df.iloc[i]['word'] not in df.iloc[i]['sentences']:
        rm_l.append(i)
df = df.drop(df.index[rm_l])

cut_time = time.time() - start_time
print('cut_time: ', cut_time)
print('total sentences:' , df.shape)
df.to_csv('../2019-12-12.article_cutsent_test.csv', index=False)


batch_size = 115
batch_ls = list(range(df.shape[0]))[0::batch_size]  
tasks = [main(df.iloc[batch_ls[i]: batch_ls[i] + batch_size], batch_size) for i in range(len(batch_ls))]  

export_path = '../2019-12-12.article_sentprob_batch115_test.csv'

loop.run_until_complete(asyncio.wait(tasks))
run_time = time.time() - start_time
print('run_time: ', run_time)
result_df = pd.read_csv(export_path)
with open('../test_run_time.txt', 'a') as f:
    f.write('Time for ' + filepath + str(result_df.shape[0]) + ' : ')
    f.write(str(round(run_time, 5))+'\n')
    f.close()
