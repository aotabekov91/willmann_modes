import os
import subprocess

from qapp.widget import InputBrowser

class Mindmap(InputBrowser):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.path=None
        self.html=None

        self.input.setLabel('Mindmap')

    def loadMindmap(self, path):

        self.browser.setHtml('<body>Creating ... </body>')
        os.popen('rm -rf /tmp/mindmap.html')
        cmd=['markmap',  '--no-open', '--no-toolbar', '-o',  f'/tmp/mindmap.html', path]
        p=subprocess.Popen(cmd)
        p.wait()
        with open(f'/tmp/mindmap.html', 'r') as f: html=f.readlines()
        html=' '.join([f.strip('\n') for f in html])

        self.path=path
        self.html=html
        self.browser.setHtml(html)

    def refresh(self, html=None):

        if not html: html=self.html
        if html: self.browser.setHtml(html)
