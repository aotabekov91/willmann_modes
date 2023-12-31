import os
import asyncio
import subprocess

from libtmux import Server
from i3ipc.aio import Connection

from qplug import PlugApp
from gizmo.widget import InputListStack

class Applications(PlugApp):

    def __init__(self, parent_port=None):

        super(Applications, self).__init__(
                 initiate_stack=False,
                 parent_port=parent_port,
                 )

        self.tmux=Server()
        self.manager=asyncio.run(Connection().connect())
        self.setUI()

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Applications')
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.hideWanted.connect(self.deactivate)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setCentered(True)

    def confirm(self):

        item=self.ui.main.list.currentItem()
        if item:
            self.deactivate()
            self.setApplication(item.itemData)

    def activate(self):

        self.applications=self.getApplications()
        self.ui.main.setList(self.applications)
        super().activate()

    def setApplication(self, item_data):

        def seti3Application(item_data):
            wid=item_data['id']
            pid=item_data.get('tmux_id', False)
            tree=asyncio.run(self.manager.get_tree())
            w=tree.find_by_id(wid)
            if w: asyncio.run(w.command('focus'))
            if not pid: return
            session, window, pane=tuple(pid.split(':'))
            os.popen(f'tmux select-pane -t "{pane}"')
            os.popen(f"tmux select-window -t '{window}'")

        seti3Application(item_data)

    def getApplications(self):

        def geti3Applications():

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

        return geti3Applications()

if __name__=='__main__':
    app=ApplicationsMode(port=33333)
    app.toggle()
    app.run()
