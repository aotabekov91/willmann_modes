import os
import re
import time

import openai

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from plugin.app.mode import AppMode

from plugin.app import register
from plugin.widget import InputBrowserStack 

class AIMode(AppMode):

    def __init__(self, port=None, parent_port=None, config=None):

        super(AIMode, self).__init__(
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.question=None
        self.answer=None

        self.setUI()
        self.setAnswerer()

    def setUI(self):

        self.ui=InputBrowserStack()
        self.ui.hideWanted.connect(self.deactivate)

        self.ui.main.input.setLabel('Question')
        self.ui.main.browser.loadCSS(self.css_path)
        self.ui.main.browser.loadHtml(self.getHtml())
        self.ui.main.returnPressed.connect(self.confirm)
        self.ui.installEventFilter(self)

        self.ui.setMaximumSize(600, 700)
        self.ui.setMinimumSize(600, 700)
        self.ui.setLocation('center')

    def toggle(self):

        if not self.ui.isVisible():
            self.activate()
        else:
            self.deactivate()

    @register('y')
    def yank(self):

        text=f'Question: \n{self.question}\nAnswer: {self.answer}'
        self.clipboard().setText(text)

    def setAnswerer(self):

        self.answerer=AIAnswer(self)
        self.answer_thread=QThread()
        self.answerer.moveToThread(self.answer_thread)
        self.answerer.answered.connect(self.update)
        self.answer_thread.started.connect(self.answerer.loop)
        QTimer.singleShot(0, self.answer_thread.start)

    @pyqtSlot(str, str)
    def update(self, question, answer):

        self.answer=re.sub(r'^\n*', '', answer)
        self.answer=re.sub(r'\n\n', '<br>', answer)
        self.ui.main.browser.loadHtml(self.getHtml(self.answer))
        self.ui.show()

    def confirm(self): 

        self.question=self.ui.main.input.text()
        self.answerer.question=self.question
        html=self.getHtml(f'{self.question} ... ')
        html=self.getHtml(self.question)
        self.ui.main.browser.loadHtml(html)

    def getHtml(self, answer=''): 

        html='''
        <!doctype html>
            <html>
                <head>
                    <title>OpenAI</title>
                </head>
                <body>
                    <p> {} </p>
                </body>
        </html>
        '''.format(answer)
        return html

class AIAnswer(QObject):
    
    answered=pyqtSignal(str, str)
    def __init__(self, parent):

        super(AIAnswer, self).__init__()
        self.parent=parent
        self.question=None
        self.completion=openai.Completion(
                api_register=os.environ['OPEN_AI_API'])

    def loop(self):

        self.running=True

        while self.running:
            if self.question:
                answer=self.get_answer(self.question)
                self.answered.emit(self.question, answer)
            self.question=None
            time.sleep(1)

    def get_answer(self, question):

        try:

            r=self.completion.create(
                prompt=question,
                model='text-davinci-003',
                # up_p=0.1,
                max_tokens=3000)

            return r['choices'][0]['text']
        except:
            return 'Could not fetch an answer from OPENAI'

if __name__=='__main__':
    app=AIMode()
    app.toggle()
    app.run()
