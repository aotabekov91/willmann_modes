import subprocess
from tables import Bookmark, Metadata, Part

from qplug import PlugApp
from qplug.utils import register
from gizmo.widget import InputListStack, InputList

class SearchMode(PlugApp):

    def __init__(self, port=None, parent_port=None, config={}):

        super(SearchMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.parts=Part()
        self.metadata=Metadata()
        self.bookmarks=Bookmark()

        self.setUI()

    def setUI(self):

        self.ui=InputListStack()
        
        self.ui.main.input.setLabel('Index')
        self.ui.main.list.returnPressed.connect(self.open)
        self.ui.main.input.returnPressed.connect(self.find)

        self.ui.addWidget(InputList(), 'bookmarks')
        self.ui.bookmarks.input.setLabel('Bookmarks')
        self.ui.bookmarks.returnPressed.connect(self.on_bookmarkConfirm)

        self.ui.addWidget(InputList(), 'parts')
        self.ui.parts.input.setLabel('Parts')
        self.ui.parts.returnPressed.connect(self.on_partConfirm)

        self.ui.addWidget(InputList(), 'documents')
        self.ui.documents.input.setLabel('Documents')
        self.ui.documents.returnPressed.connect(self.on_documentConfirm)

        self.ui.hideWanted.connect(self.deactivate)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setCentered(True)

    @register('b')
    def toggleBookmarks(self):

        if self.ui.bookmarks.isVisible():
            self.ui.show()
        else:
            self.ui.bookmarks.input.setText(self.ui.main.input.text())
            self.on_bookmarkConfirm()
            self.ui.show(self.ui.bookmarks)

    @register('d')
    def toggleDocuments(self):

        if self.ui.documents.isVisible():
            self.ui.show()
        else:
            self.ui.documents.input.setText(self.ui.main.input.text())
            self.on_documentConfirm()
            self.ui.show(self.ui.documents)

    @register('p')
    def toggleParts(self):

        if self.ui.parts.isVisible():
            self.ui.show()
        else:
            self.ui.parts.input.setText(self.ui.main.input.text())
            self.on_partConfirm()
            self.ui.show(self.ui.parts)

    @register('O')
    def openAndHide(self):

        self.open()
        self.deactivate()

    @register('o')
    def open(self):

        item=None

        if self.ui.parts.isVisible():
            item=self.ui.parts.list.currentItem()
        elif self.ui.documents.isVisible():
            item=self.ui.documents.list.currentItem()
        elif self.ui.bookmarks.isVisible():
            item=self.ui.bookmarks.list.currentItem()
        else:
            item=self.ui.main.list.currentItem()

        if item and 'id' in item.itemData:

            d=item.itemData
            kind=d['itemKind']

            if d['url']:
                os_cmd=['google-chrome-stable', d['url']]
                p=subprocess.Popen(os_cmd)

            elif d['path']:

                y=str(d.get('y1', 0))
                page=str(d.get('page', 0))

                os_cmd=['lura', '-p', page, '-y', y, d['path']]
                subprocess.Popen(os_cmd)

    def on_bookmarkConfirm(self, query=None):

        if not query: query=self.ui.bookmarks.input.text()

        blist=[]

        try:
            blist=self.bookmarks.search(query)
            for f in blist:
                f['up']=f['title']
                f['itemKind']='bookmark'
                if f['kind']=='url':
                    f['up_color']='magenta'
                elif f['path']:
                    f['up_color']='green'
        except:
            pass
                
        if not blist: 
            self.ui.bookmarks.setList([{'up': 'No match found', 'down': query}])
        else:
            self.ui.bookmarks.setList(blist)
            return blist

    def on_partConfirm(self, query=None):

        if not query: query=self.ui.parts.input.text()

        blist=[]
        try:
            blist=self.parts.search(query)
            for f in blist:
                f['up']=f['title']
                f['itemKind']='part'
                f['up_color']='yellow'
        except:
            pass

        if not blist: 
            self.ui.parts.setList([{'up': 'No match found', 'down': query}])
        else:
            blist=sorted(blist, key=lambda x: (f['path'], f['page'], f['y1']))
            self.ui.parts.setList(blist)
            return blist

    def on_documentConfirm(self, query=None):

        if not query: query=self.ui.documents.input.text()

        blist=[]
        try:
            blist=self.metadata.search(query)
            for f in blist:
                f['up']=f['title']
                f['itemKind']='document'
                f['up_color']='cyan'
        except:
            pass

        if not blist: 
            self.ui.documents.setList([{'up': 'No match found', 'down': query}])
        else:
            self.ui.documents.setList(blist)
            return blist

    def find(self):

        query=self.ui.main.input.text()

        dlist=[]
        parts=self.on_partConfirm(query)
        if parts: dlist+=parts
        documents=self.on_documentConfirm(query)
        if documents: dlist+=documents 
        bookmarks=self.on_bookmarkConfirm(query)
        if bookmarks: dlist+=bookmarks
        
        if not dlist: dlist=[{'up': 'No match found', 'down': query}]

        self.ui.main.setList(dlist)

if __name__=='__main__':
    app=SearchMode(port=33333)
    app.toggle()
    app.run()
