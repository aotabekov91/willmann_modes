#!/usr/bin/python3

import re
import bs4

from .components import save, synthesize, get_soup

def get_definition(word):
    url = f'https://www.wortbedeutung.info/{word}/'
    soup=get_soup(url)

    types=soup.find_all(text=re.compile('^\s*Wortart: .*'))
    defs=[]
    for h in types:
        dt={'word':word}
        defs+=[dt]
        h=h.previous
        m=re.search('Wortart: (\w+)\W*\W*\(*(\w+)*\)*', h.text.strip())
        if m is None: continue
        dt['function']=m.group(1)
        sound_url=soup.find('iframe')
        if sound_url is not None:
            dt['sound_url']=get_sound_url(sound_url['src'])
        else:
            dt['sound_url']=None
        if dt['function']=='Substantiv': 
           if m.group(2) and m.group(2)=='weiblich':
               dt['article']='die'
           elif m.group(2) and m.group(2)=='männlich':
               dt['article']='der'
           elif m.group(2) and m.group(2)=='sächlich':
               dt['article']='das'
        else:
            dt['article']=''
        if dt['function']=='Verb' and m.group(2):
            dt['grammar']=m.group(2)
        for section in h.next_siblings:
            if section.name=='h3': break
            if section.name!='h4': continue
            if type(section)==bs4.element.NavigableString: continue
            text=section.next.next.text
            if 'Silbentrennung' in section.text:
                dt['formen']=(text
                        .replace('|', '')
                        .replace('\n', '')
                        .replace('Präteritum: ', '')
                        .replace('Partizip II: ', '')
                        .replace('Positiv', '')
                        .replace('Komparativ', '')
                        .replace('Superlativ', '')
                        )
                if 'Mehrzahl' in dt['formen']:
                    tmp=dt['formen'].split(':')
                    if len(tmp)==2:
                        dt['plural']=tmp[1].strip()
                    elif 'Variante' in dt['formen']:
                        dt['plural']=' '.join(re.findall('Variante ([^,]*)[,]*', dt['formen']))
                    else:
                        dt['plural']=''
            elif 'Aussprache' in section.text:
                dt['ipa']=(re.search('\[(.*)\]', text)
                        .group(1)
                        .replace('[', '')
                        .replace(']', '')
                        )
            elif 'Bedeutung' in section.text:
                meanings_w={}
                meanings={}
                m_list=[]
                try:
                    m_list=section.next.next.find_all('dd')
                except:
                    try:
                        m_list= section.next.next.next.next.next.next.next.next.next.find_all('dd')
                    except:
                        pass
                for m in m_list:
                    tmp=re.search('(\d+)[)] (.*)', m.text)
                    if tmp is None: continue
                    meanings[tmp.group(1)]=tmp.group(2)
                    meanings_w[tmp.group(1)]=tmp.group(2).replace(word, ', dieses Wort, ')
                dt['meanings']=meanings
                dt['meanings_w']=meanings_w
            elif 'Anwendungsbeispiele' in section.text or 'Beispielsätze' in section.text:
                examples={}
                m_list=section.next.next.find_all('dd')
                counter={}
                for m in m_list:
                    tmp=re.search('(\d+)[)] (.*)', m.text)
                    if tmp is None: continue
                    num=tmp.group(1)
                    html_text=str(m)
                    unfilled_example=re.sub('<em>[^>]*>', ', dieses Wort, ', html_text)
                    unfilled_example=re.sub('<[^>]*>', '', unfilled_example)
                    unfilled_example=re.sub('\d+\)', '', unfilled_example)
                    if not num in examples: examples[num]={}
                    example=tmp.group(2)
                    if num in counter and counter[num]>1: 
                        continue
                    elif num in counter:
                        counter[num]+=1
                        examples[num]['example_2']=example
                        examples[num]['example_2_w']=unfilled_example
                    else:
                        counter[num]=0
                        examples[num]['example_1']=example
                        examples[num]['example_1_w']=unfilled_example
                dt['examples']=examples
            elif 'Konjugation' in section.text:
                kon_forms=section.next.next.find_all('dd')
                k_forms={}
                for k in kon_forms:
                    tmp=k.text.split(':')
                    k_forms[tmp[0]]=tmp[1]
                dt['konjugation']=k_forms
            elif 'Steigerungen' in section.text:
                dt['steigerungen']=text
    return defs

def get_anki_notes(word, deck_folder='german::daily', model_folder='Definition', **kwargs):
    run=[]
    anki_notes=[]
    notes=get_definition(word)

    for dt in notes:
        if not 'meanings' in dt: continue
        for i, (key, value) in enumerate(dt['meanings'].items()):
            note = {
                'deckName': deck_folder,
                'modelName': model_folder,
                'fields': {
                    'Word': word,
                    'Word_s':'',
                    'Language': 'German',
                    'UID': word + value + 'test',
                    'IPA': dt.get('ipa', ''),
                    'ipa': dt.get('ipa', ''),
                    'Function': dt.get('function', ''),
                    'Meaning': value,
                    'Meaning_w': dt['meanings_w'][key],
                    'Comparative': dt.get('steigerungen', ''),
                    'Gender': dt.get('article', ''),
                    'Plural': dt.get('plural', ''),
                    'Irregular': dt.get('formen', ''),
                    'Sound': dt.get('sound', ''),
                    'Grammar': dt.get('grammar', ''),
                    'Example I':'',
                    'Example I_w':'',
                    'Example I_s':'',
                    'Example I_w_s':'',
                    'Example II':'',
                    'Example II_w':'',
                    'Example II_s':'',
                    'Example II_w_s':'',
                    }
                }

            image_name, image_path=synthesize(value, lan='de', kind='image', run=run)

            note['picture']={
                'path' : image_path,
                'filename': image_name,
                'fields': ['Image']
                }
            note['picture_loc']=image_path

            note['audio']=[]
            w_n, w_p=synthesize(word, lan='de', kind='sound', run=run)
            note['audio']+=[
                {
                    'path': w_p,
                    'filename': w_n, 
                    'fields': ['Word_s', 'Sound']
                },
                ]

            w_n, w_p=synthesize(value, lan='de', kind='sound', run=run)
            note['audio']+=[
                {
                    'path': w_p,
                    'filename': w_n, 
                    'fields': ['Meaning_s']
                },
                ]


            w_n, w_p=synthesize(dt['meanings_w'][key], lan='de', kind='sound', run=run)
            note['audio']+=[
                {
                    'path': w_p,
                    'filename': w_n, 
                    'fields': ['Meaning_w_s']
                }
                ]

            if 'konjugation' in dt:
                note['fields']['Imperative']=dt['konjugation'].get('Imperativ', '')
                note['fields']['Conjunctive II']=dt['konjugation'].get('Konjunktiv II', '')
                note['fields']['Help verb']=dt['konjugation'].get('Hilfsverb', '')

            
            if 'examples' in dt:
                examples=dt['examples'].get(key, []) 
            else:
                examples=[]

            for i, example in enumerate(examples):
                s='I'*(i+1)
                if not f'example_{i+1}' in examples: break
                note['fields'][f'Example {s}']=examples[f'example_{i+1}']
                note['fields'][f'Example {s}_w']=examples[f'example_{i+1}_w']

                e_n, e_p=synthesize(examples[f'example_{i+1}'], lan='de', kind='sound', run=run)

                note['audio']+=[
                            {
                                'path': e_p, 
                                'filename': e_n,
                                'fields': [f'Example {s}_s']
                            },
                            ]

                e_n, e_p=synthesize(examples[f'example_{i+1}_w'], lan='de', kind='sound', run=run)
                note['audio']+=[
                            {
                                'path': e_p, 
                                'filename': e_n,
                                'fields': [f'Example {s}_w_s']
                            },
                            ]

            anki_notes+=[note]
    return anki_notes, run
