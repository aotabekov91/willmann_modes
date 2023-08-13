import subprocess

from plug import command
from qplug import PlugApp
from qplug.utils import register
from gizmo.widget import InputListStack

class Player(PlugApp):

    def __init__(self, parent_port=None):

        super(Player, self).__init__(
                 parent_port=parent_port)

        self.current_player=''
        self.setUI()

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Player')
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setCentered(True)

    def getPlayerList(self):

        proc=subprocess.Popen(
                ['playerctl', '-l'], stdout=subprocess.PIPE)

        data=[]
        proc=subprocess.Popen([
            'playerctl', 
            '-a', 
            'metadata', 
            '--format', 
            '{{playerName}}__::::__{{artist}}__::::__{{title}}'
            ], stdout=subprocess.PIPE)

        for i, p in enumerate(proc.stdout.readlines()):

            p=p.decode().strip('\n').split('__::::__')
            data+=[{'up':p[-1],
                    'down':'{}{}'.format(
                        p[0], f' - {p[-2]}'*bool(p[-2])),
                    'id':p[0],
                    }]
        return data

    def activate(self): 

        super().activate()
        self.ui.main.setList(self.getPlayerList())

    def confirm(self): 

        if self.ui.isVisible():
            item=self.ui.main.list.currentItem()
            if item and 'id' in item.itemData:
                self.current_player=item.itemData['id']
                self.ui.main.edit.clear()
                self.deactivate()
    
    def getCurrentPlayer(self):

        if self.current_player:
            return f' -p {self.current_player} '
        return ' '

    @register(' ')
    @command()
    def togglePlayPause(self):

        self.setPlayer()
        return f'playerctl {self.getCurrentPlayer()} play-pause'

    @register('h')
    @command()
    def next(self):

        self.setPlayer()
        return f'playerctl {self.getCurrentPlayer()} next'

    @register('l')
    @command()
    def previous(self):

        self.setPlayer()
        return f'playerctl {self.getCurrentPlayer()} previous'

    @register('i')
    @command()
    def increaseVolume(self):

        self.setPlayer()
        return 'pactl set-sink-volume 0 +5%'

    @register('d')
    @command()
    def decreaseVolume(self):

        self.setPlayer()
        return 'pactl set-sink-volume 0 -5%'

    @register('m')
    @command()
    def mute(self):

        self.setPlayer()
        return 'pactl set-sink-mute 0 toggle' 

    @register('s')
    def setPlayer(self):

        item=self.ui.main.list.currentItem()
        if item: self.current_player=item.itemData['id']

    @register('c')
    def toggleCommands(self):

        self.ui.toggleCommands()

if __name__=='__main__':
    app=Player(port=33333)
    app.toggle()
    app.run()
