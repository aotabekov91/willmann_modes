import os
import zmq
import hashlib
import playsound

from plugin.app import register
from plugin.widget import InputListStack

from tables import Joke, Quote
from plugin.app.mode import AppMode

class GeneratorMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(GeneratorMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.request={}
        self.joke=Joke()
        self.quote=Quote()

        self.setUI()
        self.setMode('sound')

    def setUI(self):

        self.ui=InputListStack()
        self.ui.main.input.setLabel('Generate')
        self.ui.main.returnPressed.connect(self.confirm)

        self.ui.installEventFilter(self)

    def setConnection(self):

        super().setConnection()
        if self.generator_port:
            self.gsocket=zmq.Context().socket(zmq.PUSH)
            self.gsocket.connect(f'tcp://localhost:{self.generator_port}')

    def setMode(self, mode):

        self.mode=mode
        self.request={}
        self.ui.main.setList([])
        self.ui.main.input.setLabel(f'{self.mode.title()}')

        if mode in ['joke', 'quote']: self.confirm()

    @register('s')
    def soundMode(self): self.setMode('sound')

    @register('i')
    def imageMode(self): self.setMode('image')

    @register('j')
    def jokeMode(self): self.setMode('joke')

    @register('x')
    def quoteMode(self): self.setMode('quote')

    def confirm(self):

        if self.mode in ['sound', 'image']:
            self.submit()
            self.refresh()

        elif self.mode=='quote':
            
            quote=self.quote.getRandomRow()
            if quote:
                data=quote[0]
                data['up']=data['text']
                data['up_color']='green'
                data['down']=data['author']

            self.ui.main.setList([data])
            self.ui.show()

        elif self.mode=='joke':

            joke=self.joke.getRandomRow()
            if joke:
                data=joke[0]
                data['up']=data['text']
                data['up_color']='green'
                if data['author']:
                    data['down']=data['author']
                else:
                    data['down']=data['name']

            self.ui.main.setList([data])
            self.ui.show()

    def submit(self):

        text=self.ui.main.input.text()
        path=f'/tmp/{hashlib.md5(text.encode()).hexdigest()}'

        request={'text':text, 'path': path} 

        if self.mode=='sound':
            request['kind']='sound'
        elif self.mode=='image':
            request['kind']='image'

        self.request=request
        self.gsocket.send_json(request)

    @register('r')
    def refresh(self):

        if self.request: 

            path=self.request['path']
            if os.path.isfile(path):
                if self.mode=='sound':
                    playsound.playsound(path, block=False)
                elif self.mode=='image':
                    dlist=[{'up':self.ui.main.input.text()(), 'icon':path}]
                    self.ui.main.setList(dlist)
                    self.ui.show()

if __name__=='__main__':
    app=GeneratorMode(port=33333)
    app.toggle()
    app.run()
