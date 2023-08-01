import os

from plug import command
from qapp.plug import PlugApp
from qapp.widget import InputListStack

class KeyboardMode(PlugApp):

    def __init__(self, port=None, parent_port=None, config=None):

        super(KeyboardMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 keyword='keyboard',
                 config=config)

        self.setUI()
        self.setKeyboards()

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Keyboard')
        self.ui.main.returnPressed.connect(self.setLanguage)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setCentered(True)

    def setKeyboards(self):

        self.keyboards=[]
        for k, d in {'English':'us', 'German':'de', 'Russian':'ru'}.items():
            self.keyboards+=[{'up':k, 'id':d}]
        self.ui.main.setList(self.keyboards)

    def setLanguage(self, lan=None):

        self.deactivate()
        if not lan:
            item=self.ui.main.list.currentItem()
            if item: lan=item.itemData.get('id', 'us')
        os.popen(f'setxkbmap {lan}')

if __name__=='__main__':
    app=KeyboardMode(port=33333)
    app.toggle()
    app.run()
