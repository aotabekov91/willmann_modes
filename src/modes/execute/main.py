import os

from qplug import PlugApp
from qplug.utils import register
from gizmo.widget import InputListStack

class ExecuteMode(PlugApp):

    def __init__(self, port=None, parent_port=None, config={}):

        super(ExecuteMode, self).__init__(
                 name='Execute', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.last_command=None
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
        self.ui.setCentered(True)

    def on_commandChanged(self):
        
        text=self.ui.main.input.text()
        self.ui.main.setList([{'up': 'Execute bash command', 'down' :text}])

    @register('l')
    def runLastCommand(self):

        if self.last_command: os.popen(self.last_command)

    def confirm(self):

        text=self.ui.main.input.text()
        self.last_command=text
        if text:
            self.ui.main.clear()
            os.popen(text)

if __name__=='__main__':
    app=ExecuteMode(port=33333)
    app.toggle()
    app.run()
