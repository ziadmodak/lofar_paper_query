# lofar_paper_query
Python script to search for LOFAR projects used in a scientific paper.

Requires `arxiv`. `ads` and `tqdm`. These packages can be installed by this command:
```
pip install arxiv ads tqdm
```

If you are not a `root` user, please use the `--user` flag.

The code takes in the DOIs of the papers, sends a query to ADS using their [API](https://github.com/adsabs/adsabs-dev-api) to retrieve the publication dates and arXiv IDs. Using these arXiv IDs, it will download the preprint of a paper to disk, search for all the mentioned LOFAR project codes in the text and tables, and then delete the paper from disk. This will be done for each paper's ID.

The output of the code is a `.csv` file containing paper title, publication date (from ADS) and the LOFAR project code used in that work.
