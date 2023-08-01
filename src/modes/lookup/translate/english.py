import re
from .components import save, synthesize, get_soup

def get_definition(word):

    if len(word.split(' '))==1:
        return get_word_definition(word)
    else:
        return get_phrase_definition(word)

def get_phrase_definition(word):

    phrase=word.replace(' ', '-')
    url = f'https://dictionary.cambridge.org/us/dictionary/english/{phrase}'
    soup=get_soup(url)
    try:
        entries=(soup
                 .find_all('div', class_='pv-block')
                 )
    except:
        entries=[]
    notes=[]
    for entry in entries:
        term=entry.find('div', class_='di-title').text
        function=entry.find('span', class_='pos dpos').text
        grammar = entry.find('span', class_="anc-info-head danc-info-head").text
        try:
            uk_ipa=(entry
                    .find('span', class_='uk dpron-i')
                    .find('span', class_='pron dpron'))
        except AttributeError:
            uk_ipa=''
        try:
            sound_url='https://dictionary.cambridge.org'+(
                    entry.find('span', class_='uk dpron-i')
                    .find('span', class_='daud')
                    .find('source')['src']
                    )
        except AttributeError:
            sound_url=''
        try:
            irregular=entry.find('span', class_='irreg-infls dinfls').text.strip()
        except:
            irregular=''
        try:
            grammar=entry.find('span', class_='gram dgram').text
            grammar=grammar.replace('[', '').replace(']', '').strip()
        except:
            grammar=''
        function=entry.find('span', class_='pos dpos').text.strip()
        p={
                'ipa':uk_ipa,
                'ipa_text':uk_ipa,
                'sound_url':sound_url,
                'sound_name': re.sub('.*/', '', sound_url),
                'function':function,
                'irregular': irregular,
                'grammar': grammar,
                'term': term,
                'image_url':'',
                'guide_word': '',
              }
        p=p.copy()
        if p['ipa']: p['ipa_text']=p['ipa'].text
        p['meaning']=(entry
                         .find('div', class_=re.compile('def .*db'))
                         .text
                         .replace('\n', ' ')
                         .replace(':', ' ')
                         .strip())
        if p['meaning'] in [i['meaning'] for i in notes]: continue
        p['meaning_w']=re.sub(p['term']+'[^ ]*', ', this word, ', p['meaning'])
        # try:
        p['examples']=[]
        p['examples_w']=[]
        for f in entry.find_all('div', class_='examp dexamp'):
            f=f.text.strip()
            p['examples']+=[f]
            p['examples_w']+=[re.sub(f'{term}[^ ]*', ', this word, ', f)]
        try:
            tmp=entry.find('div', class_='def-body ddef_b')
            tmp=tmp.find_all('div', class_='examp dexamp')
        except:
            tmp=[]
        if tmp:
            for f in tmp:
                f=f.text.strip()
                if not f in p['examples']:
                    p['examples']+=[f]
                    p['examples_w']+=[re.sub(f'{term}[^ ]*', ', this word, ', f)]
        notes+=[p]
    return notes

def get_word_definition(word):

    url = f'https://dictionary.cambridge.org/us/dictionary/english/{word}'
    soup=get_soup(url)
    try:
        entries=(soup
                 .find('div', class_='entry')
                 .find_all('div', class_='pr entry-body__el')
                 )
    except:
        entries=[]
    notes=[]


    for entry in entries:
        try:
            uk_ipa=(entry
                    .find('span', class_='uk dpron-i')
                    .find('span', class_='pron dpron'))
        except AttributeError:
            uk_ipa=''
        try:
            sound_url='https://dictionary.cambridge.org'+(
                    entry.find('span', class_='uk dpron-i')
                    .find('span', class_='daud')
                    .find('source')['src']
                    )
        except AttributeError:
            sound_url=''
        try:
            irregular=entry.find('span', class_='irreg-infls dinfls').text.strip()
        except:
            irregular=''
        try:
            grammar=entry.find('span', class_='gram dgram').text
            grammar=grammar.replace('[', '').replace(']', '').strip()
        except:
            grammar=''
        term=entry.find('span', class_=re.compile('hw .*hw')).text.strip()
        function=entry.find('span', class_='pos dpos').text.strip()
        blocks=entry.find_all('div', class_=re.compile('pr dsense.*'))
        base={
                'ipa':uk_ipa,
                'ipa_text':uk_ipa,
                'sound_url':sound_url,
                'sound_name': re.sub('.*/', '', sound_url),
                'function':function,
                'irregular': irregular,
                'grammar': grammar,
                'term': term,
                'image_url':'',
                'guide_word': '',
              }
        if uk_ipa: base['ipa_text']=uk_ipa.text
        for block in blocks:
            base_guided=base.copy()
            try:
                guide_word=block.find('span', class_=re.compile('guideword .*gw')).span.text.strip()
                base_guided['guide_word']=guide_word
            except:
                pass
            p_=block.find_all('div', class_=re.compile('pr phrase-block dphrase-block'))
            b_=block.find_all('div', class_='def-block ddef_block')
            for phrase in p_+b_:
                p=base_guided.copy()
                try:
                    p['term']=phrase.find('span', class_='phrase-title dphrase-title').text.strip()
                except:
                    pass
                p['meaning']=(block
                                 .find('div', class_=re.compile('def .*db'))
                                 .text
                                 .replace('\n', ' ')
                                 .replace(':', ' ')
                                 .strip())
                try:
                    image_url=('https://dictionary.cambridge.org'+
                               phrase.find('div', class_='dimg').find('amp-img')['src'])
                    p['image_url']=image_url
                except:
                    pass
                if p['meaning'] in [i['meaning'] for i in notes]: continue
                p['meaning_w']=re.sub(p['term']+'[^ ]*', ', this word, ', p['meaning'])
                # try:
                p['examples']=[]
                p['examples_w']=[]
                for f in phrase.find_all('div', class_='examp dexamp'):
                    f=f.text.strip()
                    p['examples']+=[f]
                    p['examples_w']+=[re.sub(f'{term}[^ ]*', ', this word, ', f)]
                try:
                    tmp=block.find('div', class_='def-body ddef_b')
                    tmp=tmp.find_all('div', class_='examp dexamp')
                except:
                    tmp=[]
                if tmp:
                    for f in tmp:
                        f=f.text.strip()
                        if not f in p['examples']:
                            p['examples']+=[f]
                            p['examples_w']+=[re.sub(f'{term}[^ ]*', ', this word, ', f)]
                notes+=[p.copy()]
    return notes

def get_anki_notes(word, deck_folder='english::daily', model_folder='Definition', **kwargs):

    run=[]
    anki_notes=[]
    notes=get_definition(word)
    for n in notes: 
        note = {
            'deckName': deck_folder,
            'modelName': model_folder,
            'fields': {
                'UID': n['term']+n['meaning']+'test',
                'Language': 'English',
                'IPA': str(n['ipa']), 
                'ipa': n['ipa_text'],
                'Word': n['term'],
                'Word_s':'',
                'Sound':'',
                'Function': n['function'],
                'Irregular': n['irregular'],
                'Grammar': n['grammar'],
                'Guide': n['guide_word'],
                'Meaning': n['meaning'],
                'Meaning_s': '',
                'Meaning_w': n['meaning_w'],
                'Meaning_w_s': '',
                'Example I':'',
                'Example I_w':'',
                'Example I_s ':'',
                'Example I_w_s ':'',
                'Example II':'',
                'Example II_w':'',
                'Example II_s':'',
                'Example II_w_s':'',
                },
            }

        note['audio']=[]

        if n['sound_url']!='':
            s_n, s_p=save(n['term'], n['sound_url'], ext='wav')
            note['audio']+=[{
                'path': s_p, 
                'filename': s_n,
                'fields': ['Sound']
                }]

        s_n, s_p=synthesize(n['term'], lan='en', kind='sound', run=run)
        note['audio']+=[{
            'path': s_p, 
            'filename': s_n,
            'fields': ['Word_s']
            }]

        m_name, m_path=synthesize(n['meaning'], lan='en', kind='sound', run=run)
        note['audio']+=[
            {
                'path': m_path,
                'filename': m_name,
                'fields': ['Meaning_s']
            },
            ]
        if n['meaning_w']!=n['meaning']:
            m_name, m_path=synthesize(n['meaning_w'], lan='en', kind='sound', run=run)
        note['audio']+=[
            {
                'path': m_path,
                'filename': m_name,
                'fields': ['Meaning_w_s']
            },
            ]

        if n['image_url']!='':
            image_name, image_path=save(n['meaning'], n['image_url'], ext='jpg')
            note['picture']={
                'path' : image_path, 
                'filename': image_name, 
                'fields': ['Image']
                }
        else:
            image_name, image_path=synthesize(n['meaning'], lan='en', kind='image', run=run)
            note['picture']={
                'path' : image_path,
                'filename': image_name,
                'fields': ['Image']
                }
        note['picture_loc']=image_path

        for i, example in enumerate(n['examples']):
            e_n, e_p=synthesize(example, kind='sound', lan='en', run=run)
            ew_n, ew_p=synthesize(n['examples_w'][i], lan='en', kind='sound', run=run)
            s="I"*(i+1)
            note['fields'][f'Example {s}']=example
            note['fields'][f'Example {s}_w']=n['examples_w'][i]

            note['audio']+=[
                        {
                        'path': e_p,
                        'filename': e_n, 
                        'fields': [f'Example {s}_s']
                        },
                        {
                        'path': ew_p,
                        'filename': ew_n, 
                        'fields': [f'Example {s}_w_s']
                        }
                        ]

        anki_notes+=[note]
    return anki_notes, run
