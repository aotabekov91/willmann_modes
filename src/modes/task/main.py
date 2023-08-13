import time
import datetime
import playsound

from PyQt5 import QtCore

from qplug import PlugApp
from qplug.utils import register
from tables import Pomodoro, Quote
from gizmo.widget import LeftRightEdit, CommandStack, InputList, ListWidget

class Timer(QtCore.QObject):

    changed=QtCore.pyqtSignal()
    workFinished=QtCore.pyqtSignal()
    restFinished=QtCore.pyqtSignal()

    def __init__(self, parent):

        super(Timer, self).__init__()

        self.parent=parent
        self.activated=False

        self.work=0
        self.rest=0
        self.paused=0
        self.cycle=0

        self.task=None
        self.mode='wait'
        self.task_name=''
        self.paused=False

    def run(self):

        while True:
            if not self.activated: 
                time.sleep(1)
            else:
                self.runTimer()

    def runTimer(self):

        for cycle in range(self.cycle):

            self.worked=0
            self.rested=0
            self.cycled=0
            self.paused=0

            self.restFinished.emit()

            while self.work>self.worked:

                self.mode='work'

                if self.activated:
                    self.worked+=1
                    self.changed.emit()
                    time.sleep(1)
                else:
                    self.mode='wait'
                    self.activated=False
                    self.workFinished.emit()
                    return

                while self.paused: 

                    self.mode='Work [paused]'
                    self.paused+=1
                    time.sleep(1)
                    self.changed.emit()

                self.paused=0

            self.workFinished.emit()

            while self.rest>self.rested:

                self.mode='rest'

                if self.activated:
                    self.rested+=1
                    self.changed.emit()
                    time.sleep(1)
                else:
                    self.mode='wait'
                    self.activated=False
                    self.restFinished.emit()
                    return

                while self.paused: 

                    self.mode='Rest [paused]'
                    time.sleep(1)
                    self.paused+=1
                    self.changed.emit()

                self.paused=0

            self.mode='Wait'
            self.cycled+=1

        self.restFinished.emit()

        self.paused=False
        self.activated=False

class TaskMode(PlugApp):

    def __init__(self, port=None, parent_port=None, config={}):

        super(TaskMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.mode=None
        self.task_data={}

        self.db=Pomodoro()
        self.quote=Quote()
        self.updateQuote(sound=False, show=False)

        self.setUI()
        self.setTimer()

    def setUI(self):

        self.ui=CommandStack()

        self.ui.addWidget(InputList(), 'tasks')
        self.ui.tasks.input.setLabel('Tasks')
        self.ui.tasks.returnPressed.connect(self.on_tasksReturnPressed)

        self.ui.addWidget(InputList(), 'progress')
        self.ui.progress.input.setLabel('Progress')

        self.ui.addWidget(InputList(item_widget=LeftRightEdit), 'task', main=True)
        self.ui.task.input.setLabel('Task')
        self.ui.task.returnPressed.connect(self.start)
        self.ui.addWidget(ListWidget(), 'status')
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setCentered(True)

    @register('a')
    def activate(self, task_data={}):

        data=[]
        task_field={'left': 'Task', 'right': ''}
        if task_data: task_field['right']=task_data['up']
        data+=[task_field]

        for f in ['Work', 'Rest', 'Cycle']:
            field={'left':f, 'data':task_data}
            field['right']=getattr(self, f.lower())
            data+=[field]

        self.task_data=task_data
        self.ui.task.setList(data)
        self.ui.show(self.ui.task)

    @register('x')
    def finish(self): self.timer.activated=False
    
    @register('p')
    def togglePause(self): 

        if self.timer.paused:
            self.timer.paused=False
        else:
            self.timer.paused=True

    def workFinished(self):

        data={'task':self.timer.task, 
              'duration':self.timer.worked, 
              'time':datetime.datetime.now()}
        self.db.pomodoros.writeRow(data)

    @register('S')
    def start(self):

        if self.timer.activated: self.finish()

        data=self.ui.task.list.dataList()

        if not self.task_data.get('id', None):

            task_name=data[0]['right']
            task={'desc': task_name}
            self.db.tasks_table.writeRow(task)
            row=self.db.tasks_table.getRow(task)
            self.task_data=row[0]
            self.task_data['up']=self.task_data['desc']

        for d in data: self.task_data[d['left']]=d['right']

        self.timer.task=self.task_data['id']
        self.timer.task_name=self.task_data['up']
        self.timer.work=float(self.task_data['Work'])*60
        self.timer.rest=float(self.task_data['Rest'])*60
        self.timer.cycle=int(self.task_data['Cycle'])

        self.timer.activated=True
        print(self.task_data)
        self.showStatus()

    def on_tasksReturnPressed(self): 

        item=self.ui.tasks.list.currentItem()
        if item: self.activate(task_data=item.itemData)

    @register('t')
    def showTasks(self):

        tlist=self.getTasks()
        self.ui.tasks.setList(tlist)
        self.ui.show(self.ui.tasks)

    @register('d')
    def delete(self):

        item=self.ui.tasks.list.currentItem()

        if item and self.ui.tasks.isVisible(): 
            task_id=item.itemData['id']
            self.db.tasks_table.removeRow({'id':task_id})
            self.showTasks()

    @register('s')
    def showStatus(self):

        self.updateStatus()
        self.ui.show(self.ui.status)

    def updateStatus(self):

        mode=self.timer.mode

        if mode=='work':
            time=self.timer.work-self.timer.worked
            color='red'
        elif mode=='rest':
            time=self.timer.rest-self.timer.rested
            color='green'
        elif mode and 'paused' in mode:
            time=self.timer.paused
            color='yellow'
        else:
            time=0
            color='cyan'

        minute, second = divmod(time, 60)
        second=str(int(second)).zfill(2)

        up= mode.title() 
        down=f'{self.timer.task_name}: {int(minute)}:{second}'

        dlist=[{'up': up, 'down': down, 'up_color':color}, self.quote_data]
        self.ui.status.setList(dlist)

    @register('P')
    def toggleProgress(self):

        if self.ui.progress.isVisible():
            self.ui.show()
        else:
            dlist=self.getProgress()
            self.ui.progress.setList(dlist)
            self.ui.show(self.ui.progress)

    def getProgress(self):

        cursor=self.db.pomodoros.execute('select * from pomodoros where date(time)>=date("now")', query=True)
        finished=cursor.fetchall()
        seconds=0.
        for f in finished: seconds+=f['duration']
        hours=str(seconds/3600.)[:3]
        return [{'up': 'Worked hours', 'down': hours, 'down_color': 'green'}]

    def setTimer(self):

        self.timer_thread=QtCore.QThread()
        self.timer=Timer(self)
        self.timer.moveToThread(self.timer_thread)

        self.timer.changed.connect(self.updateStatus)
        self.timer.workFinished.connect(self.workFinished)

        self.timer.workFinished.connect(self.updateQuote)
        self.timer.restFinished.connect(self.updateQuote)

        self.timer_thread.started.connect(self.timer.run)
        QtCore.QTimer.singleShot(0, self.timer_thread.start)

    def getTasks(self):

        data=[]
        for i, j in self.db.task_chain.items():
            if i:
                name='>'.join([self.db.tasks[t[0]].desc for t in j])
                row=self.db.tasks_table.getRow({'id': i})
                if row and name:
                    task_data=row[0]
                    task_data['up']=name
                    task_data.pop('color')
                    data+=[task_data]
        data=sorted(data, key=lambda x: x['up'])
        return data

    def updateQuote(self, sound=True, show=True): 

        quote=self.quote.getRandomRow()
        if quote:
            data=quote[0]
            data['up']=data['text']
            data['down']=data['author']
            self.quote_data=data

        else:
            self.quote_data={'up': 'Sorry, no quotes'}

        if sound: playsound.playsound(self.sound_path, block=False)
        if show: 
            self.ui.hide()
            self.showStatus()

if __name__=='__main__':
    app=TaskMode(port=8234)
    app.toggle()
    app.run()
