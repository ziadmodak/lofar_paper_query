import os
import ads      
import arxiv
import numpy as np
import pandas as pd
from tqdm import tqdm

data = pd.read_csv('paper_data.csv')

dois = [j for j in data['DOI']]

ids = [list(ads.SearchQuery(doi=j))[0].identifier for j in dois]

arxiv_list = []
for i in range(0,len(ids)):
    for k in ids[i]:
        if k[:5] == 'arXiv':
            arxiv_list.append([k[6:], i])

arxiv_list = np.array(arxiv_list)

papers = arxiv.query(id_list=arxiv_list[:,0], max_results=len(ids))

def temp_file(obj):
    return 'temp'

codes = []
for i in tqdm(papers):
    arxiv.download(i, slugify=temp_file)
    paper = list(ads.SearchQuery(title=i.title))[0] 
    hits = os.popen('pdfgrep -o "LT[0-9].{0,5}|LC[0-9].{0,5}|L[0-9][0-9][0-9][0-9][0-9]{0,2}|DDT[0-9]{0,5}" temp.pdf').read()
    codes.append(np.array([paper.title,paper.pubdate,hits.splitlines()]))
    os.system('rm temp.pdf')

codes = np.array(codes)
df = pd.DataFrame(codes)
df.to_csv('ouput_codes.csv', encoding='utf-8', index=False)
