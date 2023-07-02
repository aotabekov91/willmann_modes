import os
import bs4
import shutil
import hashlib
import requests
import urllib.parse
import fake_useragent

from multiprocessing import Process

cfolder=os.path.expanduser('~/.local/share/Anki2/kim/collection.media/')

def save(text, url, ext='jpg', check=[cfolder, ]):
    def _save(url, path):
        ua=fake_useragent.UserAgent()
        header={'User-Agent': str(ua.random)}
        r = requests.get(url, headers=header, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(path,'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print(f'File saved: {path}')
    name=f'{hashlib.md5(text.encode()).hexdigest()}.{ext}'
    for f in check:
        path=f'{f}{name}'
        if os.path.isfile(path): return name, path
    p=Process(target=_save, args=(url, path))
    p.start()
    return name, path

def synthesize(text, lan='en', kind='image', run=[], check=[cfolder, ]):
    if kind=='image':
        ext='jpg'
    elif kind=='sound':
        ext='wav'
    name=f'{hashlib.md5(text.encode()).hexdigest()}.{ext}'
    for f in check:
        path=f'{f}{name}'
        if os.path.isfile(path):
            return name, path
    run+=[{'command':'generate', 'kind':kind, 'path':path, 'text':text, 'lan':lan}]
    return name, path

def get_soup(url):
    ua=fake_useragent.UserAgent()
    header={'User-Agent': str(ua.random)}
    raw = requests.get(url, headers=header)
    if raw.status_code == 200:
        html=raw.content
        soup=bs4.BeautifulSoup(html, 'lxml')
        return soup
