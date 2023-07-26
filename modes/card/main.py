from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from plyer import notification
from ankipulator import Submitter

from plugin.app.mode import AppMode

from plugin.app import register
from plugin.widget import LeftRightEdit
from plugin.widget import InputListStack, InputList

class CardMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(CardMode, self).__init__(
                 name='Flashcard', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.decks=[]
        self.models=[]
        self.fields={}

        self.deck=None
        self.model=None

        self.submitter=Submitter()

        self.setUI()
        self.setData()

    def setUI(self):

        self.ui=InputListStack(item_widget=LeftRightEdit)

        self.ui.hideWanted.connect(self.deactivate)
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.main.list.widgetDataChanged.connect(self.on_contentChanged)

        self.ui.addWidget(InputList(), 'anki')
        self.ui.anki.returnPressed.connect(self.on_ankiReturnPressed)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setLocation('center')
        self.ui.installEventFilter(self)

    def setData(self):

        for d in self.submitter.getDecks():
            self.decks+=[{'up':d}]

        for m, flds in self.submitter.getModels().items():
            self.models+=[{'up':m}]
            self.fields[m]=flds

    def on_contentChanged(self, widget):

        field=widget.textLeft()
        value=widget.textRight()
        for data in self.ui.main.dataList():
            if data['left']==field: 
                data['right']=value
                return

    def on_ankiReturnPressed(self):

        kind=self.ui.anki.input.label()
        item=self.ui.anki.list.currentItem()
        if item:
            if kind=='Deck':
                self.deck=item.itemData['up']
            elif kind=='Model':
                self.model=item.itemData['up']
                flds=self.fields[self.model]
                data=[{'left':f, 'right':''} for f in flds]
                self.ui.main.setList(data)
            self.ui.anki.clear()
            self.activate(preserve=True)

    @register('s')
    def createShortcut(self):

        self.deck='question'
        self.model='Question'
        self.activate()

    @register('t')
    def toggleMain(self):

        if self.ui.main.isVisible():
            self.ui.show(self.ui.anki)
        else:
            self.ui.show(self.ui.main)

    @register('d')
    def showDecks(self):

        self.ui.anki.input.setLabel('Deck')
        self.ui.anki.setList(self.decks)
        self.ui.show(self.ui.anki)

    @register('m')
    def showModels(self):

        self.ui.anki.input.setLabel('Model')
        self.ui.anki.setList(self.models)
        self.ui.show(self.ui.anki)

    @register('c')
    def activate(self, preserve=False):

        self.ui.main.input.setLabel('Flashcard')
        self.ui.show(self.ui.main)
        if self.model:
            if not preserve: self.clear()
        else:
            self.showModels()

    def createNote(self):

        note={'deckName':self.deck, 'modelName':self.model}
        note['fields']={}
        for data in self.ui.main.dataList():
            note['fields'][data['left']]=data['right']
        return note

    @register('as')
    def submit(self, note=None):

        if not note: note=self.createNote()

        try:

            self.submitter.addNotes(note)
            notification.notify(title='LookupMode', message='Submitted to Anki')
            self.clear()
            self.ui.main.setFocus()

        except:
            notification.notify(title='LookupMode', message='Could not be submitted to Anki')

    def clear(self):

        flds=self.fields[self.model]
        data=[{'left':f, 'right':''} for f in flds]
        self.ui.main.setList(data)

    def confirm(self):

        if self.deck:
            if self.model:
                self.submit(self.createNote())
                self.activate()
        else:
            self.showDecks()

if __name__=='__main__':
    app=CardMode(port=33333)
    app.toggle()
    app.run()
