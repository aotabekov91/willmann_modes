from qplug import PlugApp
from gizmo.widget import InputListStack

class Moder(PlugApp):

    def __init__(self, **kwargs):

        super(Moder, self).__init__(**kwargs)

        self.setUI()
        self.modes=[]

    def setUI(self):

        self.ui=InputListStack()
        self.ui.centered=True
        self.ui.main.input.setLabel('Mode')
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.main.returnPressed.connect(self.confirm)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setCentered(True)

    def confirm(self):

        item=self.ui.main.list.currentItem()
        if item and self.parent_port:
            self.deactivate()
            self.ui.main.clear()
            mode=item.itemData.get('id')
            self.parent_socket.send_json(
                    {'command': 'setModeAction',
                     'mode':mode,
                     'action': 'activate'
                     })
            self.parent_socket.recv_json()

    def update(self, modes=[]):

        self.modes=[]
        for name, data in modes.items():
            if name!=self.__class__.__name__: 
                self.modes+=[{'up':name, 'id':name}]
        self.ui.main.setList(self.modes)

if __name__=='__main__':

    app=Moder()
    app.toggle()
    app.run()
