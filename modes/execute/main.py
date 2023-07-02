import os

from plugin.app.mode import AppMode
from plugin.widget import InputListStack

class ExecuteMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(ExecuteMode, self).__init__(
                 name='Execute', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.setUI()

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Execute')
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.main.input.textChanged.connect(self.on_commandChanged)
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setLocation('center')

    def on_commandChanged(self):
        
        text=self.ui.main.input.text()
        self.ui.main.setList([{'up': 'Execute bash command', 'down' :text}])

    def confirm(self):

        text=self.ui.main.input.text()
        if text:
            self.ui.main.clear()
            os.popen(text)

if __name__=='__main__':
    app=ExecuteMode(port=33333)
    app.toggle()
    app.run()
