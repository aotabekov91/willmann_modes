import platform
import subprocess

from qplug import PlugApp
from gizmo.widget import InputListStack 

class CommandMode(PlugApp):

    def __init__(self, port=None, parent_port=None, config={}):

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
        self.ui.setCentered(True)

    def confirm(self):

        item=self.ui.main.list.currentItem()
        if item:
            self.ui.hide()
            # Bug does not show the windows of a run application but the app is run
            subprocess.Popen(item.itemData['id'])

    def setCommands(self):

        if 'generic' in platform.release():
            cmd=['dpkg-query', '--show', r'-f=${Package}___${binary:summary}\n']
        else:
            cmd=['pacman', '-Qe']

        proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        commandlications=proc.stdout.readlines()

        commands=[]
        for command in commandlications:
            info={}
            if 'generic' in platform.release():
                command=command.decode().strip('\n').split('___')
            else:
                command=command.decode().strip('\n').split(' ')
            name=command[0]
            info['up']=name
            info['id']=name
            info['kind']='command'
            if 'generic' in platform.release():
                if len(command)>1: info['down']=command[1]
            else:
                try:
                    proc=subprocess.Popen(['whatis', '-l',  name], 
                                          stderr=subprocess.DEVNULL,
                                          stdout=subprocess.PIPE)
                    desc=proc.stdout.readline().decode()
                    desc=desc.split('-', 1)[-1].strip()
                    info['down']=desc
                except:
                    info['down']=''
            commands+=[info]

        self.commands=commands
        self.ui.main.setList(self.commands)


if __name__=='__main__':
    app=CommandMode(port=33333)
    app.toggle()
    app.run()
