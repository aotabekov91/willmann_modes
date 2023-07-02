import functools

from plugin.app import os_command
from plugin.app.mode import AppMode
from plugin.widget import InputListStack

class KeyboardMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(KeyboardMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.setUI()
        self.setKeyboards()

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Keyboard')
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.installEventFilter(self)

    def setKeyboards(self):

        self.keyboards=[]
        for k, d in {'English':'us', 'German':'de', 'Russian':'ru'}.items():
            self.keyboards+=[{'up':k, 'id':d}]
            func=functools.partial(self.setKeyboard, d)
            func.key=k[0].lower()
            setattr(self, k, func)
        self.ui.main.setList(self.keyboards)

    @os_command()
    def confirm(self):

        self.deactivate()
        item=self.ui.main.list.currentItem()
        if item:
            lan=item.itemData.get('id', 'us')
            return f'setxkbmap {lan}' 

    @os_command()
    def setKeyboard(self, lan):

        self.deactivate()
        return f'setxkbmap {lan}' 

if __name__=='__main__':
    app=KeyboardMode(port=33333)
    app.toggle()
    app.run()
