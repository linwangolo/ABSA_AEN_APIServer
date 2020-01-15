import aiohttp
import asyncio
import pandas as pd
import json
import os
import time
import re
import math

sem = asyncio.Semaphore(100)

async def make_post(session, data):
    url = 'http://10.60.10.128:6000/predict'
    # print(f'making post to {url}')
    # print(data.decode())
    async with session.post(url, data=data) as resp:
        try:
            output = await resp.json()
            result = pd.DataFrame({'sentiments':output['results']})
            result['context'] = output['context']
            result['target'] = output['target']
            if not os.path.exists(export_path):
                result.to_csv(export_path, index = False, encoding ='utf-8-sig')
            else:
                result.to_csv(export_path, mode='a', header=False, index = False, encoding ='utf-8-sig')
        except:
            pass

async def main(inputs):
    async with sem:
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[make_post(session, data = json.dumps({'target':inputs['word'],'context':inputs['sentences']}, 
                                                ensure_ascii=False).encode('utf-8'))]
            )


loop = asyncio.get_event_loop()
filepath = '../2019-12-20.article_ner.csv'
df = pd.read_csv(filepath)
df = df.drop_duplicates(subset=['sentences', 'word'], keep='last')
df = df[[i in ['ORG', 'LOC', 'PER'] for i in df['type']]] #.iloc[math.ceil(df.shape[0]/2):]   # math.ceil(df.shape[0]/2)
df_new = pd.DataFrame()
for i in range(0,df.shape[0]):
    print(i)
    content = df.iloc[i]['sentences']
    # print(content)
    if pd.isnull(content):       
        continue
    if len(content) <= 400:
        df_new = df_new.append({'word':df.iloc[i]['word'], 'sentences': content}, ignore_index = True)
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
            if df.iloc[i]['end'] < idx_cut[k]:
                df_new = df_new.append({'word':df.iloc[i]['word'], 'sentences': content[idx_cut[k-1]: idx_cut[k]]}, ignore_index = True)
                break
df = df_new
df_new.to_csv('../2019-12-20.article_cutsent.csv', index=False)

tasks = [main(df.iloc[i]) for i in range(df.shape[0])]   #df.shape[0]
export_path = '../2019-12-20.article_sentprob_test.csv'
start_time = time.time()
loop.run_until_complete(asyncio.wait(tasks))
run_time = time.time() - start_time
print('run_time: ', run_time)
with open('../test_run_time.txt', 'a') as f:
    f.write('Time for ' + filepath + str(df.shape[0]) + ' : ')
    f.write(str(round(run_time, 5))+'\n')
    f.close()
