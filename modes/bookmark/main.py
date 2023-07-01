import os
import time
import asyncio
import subprocess

from tables import Bookmark
from plugin.app.mode import AppMode 

from plugin.app import register
from plugin.widget import LeftRightEdit, InputListStack, InputList

class BookmarkMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(BookmarkMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.table=Bookmark()
        self.setUI()

    def setUI(self):

        self.ui=InputListStack(item_widget=LeftRightEdit)

        self.ui.main.input.setLabel('Bookmark')
        self.ui.main.list.widgetDataChanged.connect(self.on_contentChanged)

        self.ui.addWidget(InputList(), 'choose')
        self.ui.choose.input.setLabel('Choose')
        self.ui.choose.returnPressed.connect(self.on_chooseConfirm)

        self.ui.addWidget(InputList(), 'search')
        self.ui.search.input.setLabel('Search')
        self.ui.search.list.returnPressed.connect(self.open)
        self.ui.search.input.returnPressed.connect(self.on_searchInputConfirm)

        self.ui.addWidget(InputList(), 'browser')
        self.ui.browser.input.setLabel('Browser')
        self.ui.browser.returnPressed.connect(self.on_browserConfirm)

        self.ui.installEventFilter(self)

    def on_searchInputConfirm(self):

        query=self.ui.search.input.text()
        founds=[]
        try:
            founds=self.table.search(query)
            for f in founds:
                f['up']=f['id']
                f['down']=f['title']
        except:
            pass

        if not founds:
            founds=[{'up': 'No match found', 'down': query}]
        self.ui.search.setList(founds)

    @register('o')
    def open(self):

        if self.ui.search.isVisible():
            item=self.ui.search.list.currentItem()
            if item: 
                os_cmd=['google-chrome-stable', item.itemData['url']]
                subprocess.Popen(os_cmd)

    @register('e')
    def edit(self):

        if self.ui.search.isVisible():
            item=self.ui.search.list.currentItem()
            if item: self.chooseUrl(item.itemData['url'])

    def on_contentChanged(self, widget):

        data=widget.data
        bid=data['id']
        field=data['left']
        value=widget.textRight()
        self.table.updateRow({'id':bid}, {field:value})

    def on_browserConfirm(self):

        item=self.ui.browser.list.currentItem()
        if item: self.yankUrl(item.itemData['id'])

    def on_chooseConfirm(self): 

        item=self.ui.choose.list.currentItem()
        if item: self.chooseUrl(item.itemData['up'])

    def chooseUrl(self, url):

        data={'url': url, 'kind': 'url'}
        rows=self.table.getRow(data)
        if not rows: 
            self.table.writeRow(data)
            rows=self.table.getRow(data)
        data=rows[0]

        dlist=[]
        for f in ['id', 'title', 'url']:
            d={}
            d['left']=f.title()
            d['right']=data[f]
            d['id']=data['id']
            dlist+=[d]

        self.ui.main.setList(dlist)
        self.ui.show(self.ui.main)

    def activate(self): self.paste()
        
    @register('b')
    def bookmark(self): self.chooseUrl(self.paste())

    @register('s')
    def toggleSearch(self):

        if self.ui.search.isVisible(): 
            self.ui.show()
        else:
            self.ui.show(self.ui.search)

    @register('d')
    def remove(self):

        if self.ui.search.isVisible():
            item=self.ui.search.list.currentItem()
            if item:
                bid=item.itemData['id']
                self.table.removeRow({'id':bid})
                rows=self.table.getAll()
                for row in rows:
                    row['up']=row['id']
                    row['down']=row['title']
                self.ui.search.setList(rows)

    @register('a')
    def showAll(self): 

        tree=asyncio.run(self.manager.get_tree())
        items=[]
        for window in tree:
            kind=window.ipc_data.get('window_properties', {}).get('class', None)
            if kind in ['qutebrowser', 'Google-chrome']:
                items+=[{'up':window.name, 'id':window.id}]
        self.ui.browser.setList(items)

        self.ui.show(self.ui.browser)

    @register('p')
    def paste(self):

        text=self.clipboard().text()
        dlist=[{'up': text}]
        self.ui.choose.setList(dlist)
        self.ui.show(self.ui.choose)

        return text

    def yankUrl(self, window_id):

        tree=asyncio.run(self.manager.get_tree())
        focused=tree.find_focused()
        workspaces=asyncio.run(self.manager.get_workspaces())
        visible=[w for w in workspaces if w.visible]
        window=tree.find_by_id(window_id)
        kind=window.ipc_data.get('window_properties', {}).get('class', None)

        if kind in ['qutebrowser', 'Google-chrome']:

            asyncio.run(window.command('focus'))
            time.sleep(0.01)
            if kind=='Google-chrome':
                os.popen('xdotool key ctrl+l key ctrl+c')
                time.sleep(0.01)
            elif kind=='qutebrowser':
                os.popen('xdotool type yy')
                time.sleep(0.01)

            for v in visible: asyncio.run(
                    self.manager.command(f'workspace {v.name}'))
            asyncio.run(focused.command('focus'))

        self.paste()

if __name__=='__main__':
    app=BookmarkMode(port=33333)
    app.toggle()
    app.run()
