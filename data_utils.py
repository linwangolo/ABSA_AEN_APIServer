# -*- coding: utf-8 -*-
# file: data_utils.py
# author: linwang <linwang071993@gmail.com>
# Copyright (C) 2020. All Rights Reserved.

def cut_sentence(article_ls, sent_num):
    article_c_ls = []
    for content in article_ls:
        if content == '':       
            continue
        start = 0
        # start_time = time.time()
        sent_ls = []
        while start+sent_num-1 < len(content):
            p = ['。','!','！','?','？',' ', '.']
            idx = max([content[start:start+sent_num-1].rfind(x) for x in p])
            if idx == -1:
                p = [',','，','：',':','、',';','；','「','」','(','〈',')','〉','《','》','〈','〉','『','』']
                idx = max([content[start:start+sent_num].rfind(x) for x in p])
            if idx == -1:
                idx = start+sent_num
            else:
                idx = start+idx
            sent_ls.append(content[start:idx])
            start =  idx +1
        # print('while loop: ', time.time()-start_time)
        if content[start:] != '':
            sent_ls.append(content[start-1:])
        article_c_ls.append(sent_ls)
    return article_c_ls

def find_target(art_ls, target):
    data_pair = []
    art_index = 0
    for art in art_ls:
        for sen in art:
            if sen.rfind(target) != -1:
                data_pair.append({'target':target, 'context': sen, 'art_index':art_index})
        art_index += 1
    return data_pair
