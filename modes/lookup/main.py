import os
import zmq
import subprocess

import playsound
from plyer import notification

from ankipulator import Submitter

from qapp.utils import register
from qapp.plug import PlugApp
from qapp.widget import InputListStack, ListWidget, Icon

from .translate import en_translation, de_translation

class LookupMode(PlugApp):

    def __init__(self, port=None, parent_port=None, config=None):

        super(LookupMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.word=None
        self.notes=None
        self.submitter=None

        self.setUI()
        self.setLan('en')
        self.submitter=Submitter()

    def setUI(self):

        self.ui=InputListStack()

        self.ui.main.returnPressed.connect(self.translate)
        self.ui.main.inputTextChanged.connect(self.on_inputTextChanged)
        self.ui.addWidget(ListWidget(item_widget=Icon), 'icon')
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setLocation('center')

    def on_inputTextChanged(self):

        self.setLan(self.lan)
        text=self.ui.main.input.text()
        dlist=[{'up': 'Look up ...', 'down': text}]
        self.ui.main.setList(dlist)

    def setConnection(self):

        super().setConnection()
        if self.generator_port:
            self.gsocket=zmq.Context().socket(zmq.PUSH)
            self.gsocket.connect(f'tcp://localhost:{self.generator_port}')

    def setLan(self, lan):

        if lan:
            self.lan=lan
            self.ui.main.input.setLabel(f'Word [{self.lan}]')

    @register('i')
    def toggleIcon(self):

        if self.ui.icon.isVisible():
            self.ui.show()
        else:
            item=self.ui.main.list.currentItem()
            if item: 
                self.ui.icon.setList([item.itemData])
                self.ui.show(self.ui.icon)

    @register('as')
    def submit(self):

        if self.notes:

            try:
                self.submitter.addNotes(self.notes)
                notification.notify(title='LookupMode', message='Submitted to Anki')
            except:
                notification.notify(title='LookupMode', 
                                    message='Could not submit to Anki', 
                                    timeout=0)

    @register('r')
    def refresh(self): self.setData(self.notes)

    @register('y')
    def yankSelected(self): 
        p=subprocess.Popen('xclip -o'.split(' '), stdout=subprocess.PIPE)
        try:
            selection=p.stdout.readlines()[0].decode()
            self.ui.main.input.setText(selection)
            self.translate()
        except:
            pass

    def lookupWord(self, request={}):

        lan=request.get('lan', self.lan)
        term=request.get('term', self.ui.main.input.text())

        if lan=='en':
            notes, run = en_translation(term)
        elif lan=='de':
            notes, run = de_translation(term)

        for r in run: self.gsocket.send_json(r)

        return notes

    def translate(self, request={}):

        self.notes=self.lookupWord(request)

        if not self.ui.isVisible(): self.ui.show()

        if self.notes:
            self.setLabel(self.notes)
            self.setData(self.notes)
        elif self.notes is None:
            dlist=[{'up':'Anki server is not running'}]
            self.ui.main.setList(dlist)
        elif len(self.notes)==0:
            dlist=[{'up':'The word is not found', 'down': self.ui.main.input.text()}]
            self.ui.main.setList(dlist)

    def setLabel(self, notes):

        if notes:
            word=notes[0]['fields']['Word']
            ipa=notes[0]['fields']['IPA']
            gender=notes[0]['fields'].get('Gender', '')
            plural=notes[0]['fields'].get('Plural', '')
            g_s=" "*bool(gender)
            p_s=" "*bool(plural)
            i_s=" "*bool(ipa)
            label=f"{gender}{g_s}{word}{p_s}{plural}{i_s}{ipa}"
            self.ui.main.input.setLabel(label)

    def setData(self, notes):

        self.dlist=[]
        for n in notes:
            icon_file=n.get('picture_loc')
            s_pron=self.getPath(n)
            s_down=self.getPath(n, 'example')
            s_up=self.getPath(n, 'meaning')
            self.dlist+=[{'up':n['fields']['Meaning'],
                          'up_color': 'yellow', 
                          'down': n['fields'].get('Example I'), 
                          'icon': icon_file, 
                          'sound_pronunciation': s_pron, 
                          'sound_down': s_down, 
                          'sound_up': s_up, 
                          'note': n, 
                          }]
        self.ui.main.setList(self.dlist)

    @register('e')
    def englishLookup(self):

        self.setLan('en')
        text=self.ui.main.input.text()
        self.ui.main.clear()
        self.ui.main.input.setText(text)

    @register('g')
    def germanLookup(self):

        self.setLan('de')
        text=self.ui.main.input.text()
        self.ui.main.clear()
        self.ui.main.input.setText(text)

    @register('sm')
    def meaningSound(self, block=False):

        item=self.ui.main.list.currentItem()
        if item:
            path=item.itemData.get('sound_up', None)
            if path and os.path.isfile(path): playsound.playsound(path, block)

    @register('sw')
    def wordSound(self, block=False):

        item=self.ui.main.list.currentItem()
        if item:
            path=item.itemData.get('sound_pronunciation', None)
            if path and os.path.isfile(path): playsound.playsound(path, block)

    @register('sx')
    def example(self, block=False):

        item=self.ui.main.list.currentItem()
        if item:
            path=item.itemData.get('sound_down', None)
            if path and os.path.isfile(path): playsound.playsound(path, block)

    def getPath(self, n, kind='pronunciation'):

        sounds_list=n.get('audio')
        if len(sounds_list)>0:
            if kind=='pronunciation':
                for f in sounds_list:
                    if 'Word_s' in f['fields']: return f['path']
            elif kind=='example':
                for f in sounds_list:
                    if 'Example I_s' in f['fields']: return f['path']
            elif kind=='meaning':
                for f in sounds_list:
                    if 'Meaning_s' in f['fields']: return f['path']



if __name__ == '__main__':
    app = LookupMode(port=33333)
    app.toggle()
    app.run()
