import subprocess

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from plugin import command

from qapp.plug import PlugApp
from qapp.utils import register
from qapp.widget import InputListStack

class PlayerMode(PlugApp):

    def __init__(self, port=None, parent_port=None, config=None):

        super(PlayerMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.current_player=''
        self.setUI()

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Player')
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setLocation('center')

    def getPlayerList(self):

        proc=subprocess.Popen(['playerctl', '-l'], stdout=subprocess.PIPE)
        players=[p.decode().strip('\n') for p in proc.stdout.readlines()]

        data=[]
        proc=subprocess.Popen(
                ['playerctl', '-a', 'metadata', '--format',
                 '{{playerName}}__::::__{{artist}}__::::__{{title}}'],
                stdout=subprocess.PIPE)
        for i, p in enumerate(proc.stdout.readlines()):
            p=p.decode().strip('\n').split('__::::__')
            data+=[{'up':p[-1],
                    'down':'{}{}'.format(p[0], f' - {p[-2]}'*bool(p[-2])),
                    # 'id':players[i],
                    'id':p[0],
                    }]
        return data

    def activate(self): 

        self.ui.main.setList(self.getPlayerList())
        self.ui.show()

    def toggle(self):

        if not self.ui.isVisible():
            self.activate()
        else:
            self.deactivate()

    def confirm(self): 

        if self.ui.isVisible():
            item=self.ui.main.list.currentItem()
            if item and 'id' in item.itemData:
                self.current_player=item.itemData['id']
                self.ui.clear()
                self.ui.hide()
    
    def getCurrentPlayer(self):

        if self.current_player:
            return f' -p {self.current_player} '
        return ' '

    @register(Qt.Key_Space)
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
        return f'pactl set-sink-mute 0 toggle' 

    @register('s')
    def setPlayer(self):

        item=self.ui.main.list.currentItem()
        if item: self.current_player=item.itemData['id']

    @register('c')
    def toggleCommands(self):

        self.ui.toggleCommands()

if __name__=='__main__':
    app=PlayerMode(port=33333)
    app.toggle()
    app.run()
