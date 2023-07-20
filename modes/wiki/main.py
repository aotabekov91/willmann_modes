import os
import re

import markdown
import fileinput
import subprocess
from lxml import etree

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from tables import WikiIndex

from plugin.app import register
from plugin.app.mode import AppMode 
from plugin.widget import InputListStack, InputList

from .network import Network
from .mindmap import Mindmap

class WikiMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(WikiMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.index=WikiIndex()

        self.setUI()

        self.setTodos()
        self.setWikis()

    def setSettings(self):

        super().setSettings()
        self.wiki_folder=os.path.expanduser(self.wiki_folder)

    def setUI(self):

        self.ui=InputListStack()

        self.ui.main.input.setLabel('Wiki')
        self.ui.main.returnPressed.connect(self.open)

        self.todos=InputList()
        self.todos.input.setLabel('Todos')
        self.todos.returnPressed.connect(self.open)
        
        self.search=InputList()
        self.search.input.setLabel('Search')
        self.search.list.returnPressed.connect(self.on_searchListConfirm)
        self.search.input.returnPressed.connect(self.on_searchInputConfirm)

        self.network=Network()
        self.network.returnPressed.connect(self.open)
        self.network.inputTextChanged.connect(self.on_networkInputTextChanged)
        self.network.browser.loadCSS(self.css_path)
        # self.network.browser.page().setBackgroundColor(Qt.white)

        self.mindmap=Mindmap()
        self.mindmap.inputTextChanged.connect(self.on_mindmapInputTextChanged)
        self.mindmap.browser.loadCSS(self.css_path)
        # self.mindmap.browser.page().setBackgroundColor(Qt.white)

        self.ui.addWidget(self.todos, 'todos')
        self.ui.addWidget(self.search, 'search')
        self.ui.addWidget(self.network, 'network')
        self.ui.addWidget(self.mindmap, 'mindmap')

        self.ui.resizeEventOccurred.connect(self.mindmap.refresh)
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setLocation('center')

    def on_mindmapInputTextChanged(self): pass

    def on_networkInputTextChanged(self):

        text=self.network.input.text()
        self.ui.main.input.setText(text)
        tlist={t['path']:t for t in self.ui.main.filterList()}
        if text=='':
            dlist=tlist
        else:
            dlist={}
            for m, v in tlist.items():
                cond=text.lower() in m.lower() or text.lower() in v['tags']
                if cond: dlist[m]=v
        self.network.renderGraphHtml(dlist)

    def on_searchInputConfirm(self):

        query=self.ui.search.input.text()
        dlist=[]
        try:
            founds=self.index.search(query)
            for f in founds:
                data={'up':f['title'], 'path':f['path'], 'line': 0}
                dlist+=[data]
        except:
            pass

        if not dlist:
            dlist=[{'up': 'No match found', 'down': query}]
        self.ui.search.setList(dlist)

    def on_searchListConfirm(self): self.open(self.search.list.currentItem())

    @register('x')
    def finishTodo(self):

        if self.ui.todos.isVisible():
            item=self.ui.main.list.currentItem()
            line=item.itemData['line']
            path=item.itemData['path']

            # Todo: Should just change one line; the code below does it for all 
            # lines in the file which is not necessary; there should be 
            # another way of doing it. Also, it seems not to work either.

            data=[]
            for l in fileinput.input(path, inplace=True):
                data+=[(fileinput.filelineno(), l, type(l))]
                l=l.strip('\n')
                if item.itemData['up'] in l:
                    new_line=l.replace('[ ]', '[x]')
                    print(new_line)
                else:
                    print(l)
            print(line, item.itemData['up'], data) # print should be kept

            self.setTodos()

    @register('o')
    def open(self, item=None): 

        if not item: 
            if self.ui.search.isVisible():
                item=self.ui.search.list.currentItem()
            elif self.ui.todos.isVisible():
                item=self.ui.todos.list.currentItem()
            else:
                item=self.ui.main.list.currentItem()
                

        if item:
            line=item.itemData.get('line', '0')
            path=item.itemData['path']
            os_cmd=['kitty', '--class', 'floating', 'vim', f'+{line}', path]
            p=subprocess.Popen(os_cmd)
            self.ui.hide()

    @register('s')
    def toggleSearch(self): 

        if self.ui.search.isVisible():
            self.ui.show()
        else:
            self.ui.show(self.ui.search)

    @register('m')
    def toggleMindmap(self): 

        if self.mindmap.isVisible():
            self.ui.show()
        else:
            if self.search.isVisible():
                item=self.search.list.currentItem()
            else:
                item=self.ui.main.list.currentItem()
            if item:
                self.mindmap.loadMindmap(item.itemData['path'])
                self.ui.show(self.mindmap)

    @register('g')
    def toggleGraph(self): 

        if self.network.isVisible():
            # self.ui.setMaximumSize(600, 700)
            # self.ui.setMinimumSize(600, 700)
            # self.ui.setLocation('center')
            self.ui.show()
        else:
            text=self.ui.main.input.text()
            self.network.input.setText(text)
            # self.ui.setMaximumSize(500, 500)
            # self.ui.setMinimumSize(500, 500)
            # self.ui.setLocation('center')
            self.ui.show(self.network)

    @register('t')
    def toggleTodos(self): 

        if self.ui.todos.isVisible():
            self.ui.show()
        else:
            self.ui.show(self.ui.todos)

    def getWikis(self, wiki_folder=None, ext='wk'):

        def setWikiLinks(lines):

            folders=[l['folder'] for l in lines.values()]
            for path, line in lines.items():
                filePath=line['path']
                line['links']=[]

                with open(filePath, 'r') as current_file:
                    md_data = current_file.read().replace('\n',' ')
                    try:
                        doc = etree.fromstring(markdown.markdown(md_data))
                    except:
                        continue
                    for link in doc.xpath('//a'):
                        link_target = link.get('href')
                        temp_name = f"{link_target}.wk"
                        for d in folders:
                            path=f'{d}/{temp_name}'
                            if os.path.isfile(path):
                                line['links']+=[path]
            return lines

        def run(path, lines={}, ext='wk'):
            if os.path.isfile(path):
                if not path.endswith(ext): return
                if not path.split('/')[-1].startswith('.'):
                    split=path.split('/')
                    title=split[-1]
                    folder='/'.join(split[:-1])
                    title=title.replace('/', '>').split('.')[0]
                    if title.startswith('>'): title=title[1:]

                    if not self.index.search(f'path:"{path}"'):
                        self.index.addWiki(path)

                    lines[path]={'path':path,
                             'up':title, 
                             'folder': folder,  
                             'tags': [folder],
                             'down': folder, 
                             'line':0,}
            else:
                for d in os.listdir(path): run(os.path.join(path, d), lines)
            return lines

        files=run(self.wiki_folder)
        lines=setWikiLinks(files)
        return lines

    @register('uw')
    def setWikis(self):

        lines=self.getWikis()
        self.wikis=lines.values()
        self.ui.main.setList(self.wikis)

    @register('ut')
    def setTodos(self):

        todos=[]
        wikis=self.getWikis()
        for d in wikis.values():
            if not d['path'].endswith('.wk'): continue
            with open(d['path'], 'r') as f:
                lines=f.readlines()
                for i, line in enumerate(lines):
                    if not re.match('.*\[[^x]\].*', line): continue
                    line=re.sub('^[^[]*', '', line)
                    data={}
                    data['up']=line.strip('\n')
                    data['down']=d['path'].split('/')[-1]
                    data['line']=i+1
                    data['path']=d['path']
                    todos+=[data]
        self.todos=sorted(todos, key=lambda x: x['down'])
        self.ui.todos.setList(self.todos)

if __name__=='__main__':
    app=WikiMode(port=8234)
    app.toggle()
    app.run()
