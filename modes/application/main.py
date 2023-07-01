import os
import asyncio
import threading
import subprocess

import libtmux
from i3ipc.aio import Connection

from plugin.app.mode import AppMode
from plugin.app import register
from plugin.widget import InputListStack, InputList, Item

class ApplicationsMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(ApplicationsMode, self).__init__(
                 name='Applications', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.tmux=libtmux.Server()
        self.manager=asyncio.run(Connection().connect())

        self.setUI()
        self.getCommands()
        self.setMode('Applications')


    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Applications')
        self.ui.main.returnPressed.connect(self.confirm)

        self.ui.addWidget(InputList(), 'command')
        self.ui.command.input.setLabel('Execute')
        self.ui.command.returnPressed.connect(self.execute)
        self.ui.command.input.textChanged.connect(self.on_commandChanged)

        self.ui.hideWanted.connect(self.deactivate)
        self.ui.installEventFilter(self)

    @register('e')
    def toggleCommand(self):

        if self.ui.command.isVisible():
            self.ui.show()
        else:
            self.ui.show(self.ui.command)

    def on_commandChanged(self):
        
        text=self.ui.command.input.text()
        self.ui.command.setList([{'up': 'Execute command', 'down' :text}])

    def execute(self):

        text=self.ui.command.input.text()
        self.ui.command.clear()
        os.popen(text)

    @register('a')
    def showApplications(self):

        self.setMode('Applications')
        self.ui.show()

    @register('c')
    def showCommands(self):

        self.setMode('Commands')
        self.ui.show()

    def setMode(self, mode):

        self.ui.main.input.setLabel(mode)
        if mode=='Applications': 
            dlist=self.getApplications()
        elif mode=='Commands':
            dlist=self.commands
        self.ui.main.setList(dlist)

    def toggle(self):

        if not self.ui.isVisible():
            self.activate()
        else:
            self.deactivate()

    def open(self, request):

        slot_names=request['slots']
        app=slot_names.get('app', None)
        if app=='ranger':
            os.popen('kitty ranger')
        elif app=='mpv':
            os.popen('mpv ~/sciebo/music')
        else:
            os.popen(app)

    def confirm(self):

        item=self.ui.main.list.currentItem()
        kind=item.itemData.get('kind', None)
        if kind:
            self.ui.hide()
            if item.itemData['kind']=='command':
                # Bug does not show the windows of a run application but the app is run
                subprocess.Popen(item.itemData['id'])
            else:
                self.setApplication(item.itemData)

    def setApplication(self, item_data):

        wid=item_data['id']
        pid=item_data.get('tmux_id', False)
        tree=asyncio.run(self.manager.get_tree())
        w=tree.find_by_id(wid)
        if w: asyncio.run(w.command('focus'))
        if not pid: return
        session, window, pane=tuple(pid.split(':'))
        os.popen(f'tmux select-pane -t "{pane}"')
        os.popen(f"tmux select-window -t '{window}'")

    def getApplications(self):

        tree=asyncio.run(self.manager.get_tree())
        items=[]
        for i3_window in tree:
            if i3_window.name in ['', None]: continue
            if i3_window.type!='con': continue
            if i3_window.name in ['content']+[str(i) for i in range(0, 11)]: continue
            if 'i3bar' in i3_window.name: continue
            workspace=i3_window.workspace().name
            if i3_window.name=='tmux':
                cmd=('list-panes', '-a', '-F',
                     '#{session_id}:#{window_id}:#{pane_id}:#{pane_pid}')
                r=self.tmux.cmd(*cmd)
                for pane_data in r.stdout:
                    pane_id, pid=tuple(pane_data.rsplit(':', 1))
                    cmd=f'ps -o cmd --no-headers --ppid {pid}'.split(' ')
                    w=subprocess.Popen(cmd, stdout=subprocess.PIPE)
                    processes=w.stdout.readlines()
                    if len(processes)>0:
                        command=processes[-1].decode().strip('\n')
                        items+=[{'up':command,
                                 'down':f'Workspace {workspace}: [tmux]',
                                 'id': i3_window.id, 
                                 'tmux_id': pane_id, 
                                 'kind':'application'}]
            else:
                items+=[{'up':i3_window.name,
                         'down':f'Workspace {workspace}',
                         'id':i3_window.id,
                         'kind':'application'}]
        return items

    def getCommands(self):

        def _commands():
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
                command_version=' '.join(command[1:])
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

        t=threading.Thread(target=_commands)
        t.deamon=True
        t.start()

if __name__=='__main__':
    app=ApplicationsMode(port=33333)
    app.toggle()
    app.run()
