import os
import ads      
import arxiv
import numpy as np
import pandas as pd
from tqdm import tqdm

data = pd.read_csv('paper_data.csv')

dois = [j for j in data['DOI']]

ads_data = [list(ads.SearchQuery(doi=j, fl=['title', 'pubdate', 'identifier']))[0] for j in dois]

unpacked_data = []
for i in ads_data:
    unpacked_data.append([i.title, i.pubdate, i.identifier])

unpacked_data = np.array(unpacked_data)
unpacked_titles = unpacked_data[:,0]
unpacked_pubdates = unpacked_data[:,1]
unpacked_identifiers = unpacked_data[:,2]


arxiv_list = []
for i in range(0,len(unpacked_identifiers)):
    for k in unpacked_identifiers[i]:
        if k[:5] == 'arXiv':
            arxiv_list.append([k[6:], i])

arxiv_list = np.array(arxiv_list)

#final titles and pubdates
paper_titles = []
paper_pubdates = []
for i in arxiv_list[:,1]:
    paper_titles.append(unpacked_titles[i.astype(np.int)])
    paper_pubdates.append(unpacked_pubdates[i.astype(np.int)])

arxiv_papers = arxiv.query(id_list=arxiv_list[:,0], max_results=len(unpacked_identifiers))

def temp_file(obj):
    return 'temp'

codes = []
for i in tqdm(range(len(arxiv_papers))):
    arxiv.download(arxiv_papers[i], slugify=temp_file)
    # paper = list(ads.SearchQuery(title=i.title))[0] 
    hits = os.popen('pdfgrep -o "LT[0-9].{0,5}|LC[0-9].{0,5}|L[0-9][0-9][0-9][0-9][0-9].{0,2}|DDT[0-9].{0,5}" temp.pdf').read()
    codes.append(np.array([paper_titles[i],paper_pubdates[i],hits.splitlines()]))
    os.system('rm temp.pdf')

codes = np.array(codes)
df = pd.DataFrame(codes)
df.to_csv('ouput_codes.csv', encoding='utf-8', index=False)
