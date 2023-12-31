from plug import command

from qplug import PlugApp
from qplug.utils import register
from gizmo.widget import InputListStack

from .util import translate

class Translator(PlugApp):

    def __init__(self, port=None, parent_port=None, config={}):

        super(Translator, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.setUI()
        self.setLan('de')

    def setUI(self):

        self.ui=InputListStack()
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.main.inputTextChanged.connect(self.on_inputTextChanged)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setCentered(True)

    def on_inputTextChanged(self):

        self.ui.main.list.clear()
        self.ui.main.setList([{'up': self.ui.main.input.text()}])

    def setLan(self, lan):

        if lan:
            self.to_lan=lan
            self.ui.main.input.setLabel(f'Translator [{self.to_lan}]:')

    def setLanguage(self, request={}):

        slot_names=request['slot_names']
        self.setLan(slot_names.get('lan', 'en'))

    def toggle(self):

        if not self.ui.isVisible():
            self.activate()
        else:
            self.deactivate()

    @register('y')
    def yank(self, request={}):

        item=self.ui.main.list.currentItem()
        if item:
            text=item.itemData['up']
            self.clipboard().setText(text)

    @register('e')
    def toEnglish(self): 

        self.setLan('en')
        self.ui.main.clear()
        self.ui.show()

    @register('g')
    def toGerman(self):

        self.setLan('de')
        self.ui.main.clear()
        self.ui.show()

    @register('c')
    def toggleCommands(self):

        self.ui.toggleCommands()

    def confirm(self):

        text=self.ui.main.input.text()
        print(text, self.to_lan)
        trans=translate(text, self.to_lan)
        dlist=[{'up':trans}]
        self.ui.main.setList(dlist)
        self.ui.show()

if __name__=='__main__':
    app=Translator(port=33333)
    app.toggle()
    app.run()
