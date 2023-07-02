import subprocess

from plugin.app.mode import AppMode
from plugin.widget import InputListStack 

class CommandMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(CommandMode, self).__init__(
                 name='Commands', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.setUI()
        self.setCommands()

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Command')
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setLocation('center')

    def confirm(self):

        item=self.ui.main.list.currentItem()
        if item:
            self.ui.hide()
            # Bug does not show the windows of a run application but the app is run
            subprocess.Popen(item.itemData['id'])

    def setCommands(self):

        def getArchCommands():
            proc=subprocess.Popen(['pacman', '-Qe'], 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL
                                  )
            commandlications=proc.stdout.readlines()
            commands=[]
            for command in commandlications:
                info={}
                command=command.decode().strip('\n').split(' ')
                command_name=command[0]
                info['up']=command_name
                info['id']=command_name
                info['kind']='command'
                try:
                    proc=subprocess.Popen(['whatis', '-l',  command_name], 
                                          stderr=subprocess.DEVNULL,
                                          stdout=subprocess.PIPE)
                    desc=proc.stdout.readline().decode()
                    desc=desc.split('-', 1)[-1].strip()
                    info['down']=desc
                except:
                    info['down']=''
                commands+=[info]
            self.commands=commands

        
        getArchCommands()
        self.ui.main.setList(self.commands)

if __name__=='__main__':
    app=CommandMode(port=33333)
    app.toggle()
    app.run()
