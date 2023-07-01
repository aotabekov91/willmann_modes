from plugin.app.mode import AppMode
from plugin.widget import InputListStack

class Moder(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(Moder, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.setUI()
        self.modes=[]

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Mode')
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.installEventFilter(self)

    def confirm(self):

        item=self.ui.main.list.currentItem()
        if item and self.parent_port:
            self.ui.hide()
            self.ui.main.clear()
            mode=item.itemData.get('id')
            self.parent_socket.send_json(
                    {'command': 'setModeAction',
                     'mode':mode,
                     'action': 'activate',
                     })
            self.parent_socket.recv_json()

    def update(self, request):

        slots=request.get('slots', {})
        modes=slots.get('modes', [])
        if modes:
            self.modes=[]
            for name, data in modes.items():
                if name!=self.__class__.__name__: self.modes+=[{'up':name, 'id':name}]
            self.ui.main.setList(self.modes)
