from plugin.widget import InputBrowser
from pyvis.network import Network as Graph

class Network(InputBrowser):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.input.setLabel('Network')

    def renderGraphHtml(self, dlist=None):

        if dlist is None: dlist=self.dlist
        size=self.browser.size()
        height='400px'
        height=f'{size.height()-30}px'
        nx_network=Graph(height=height, width="100%", bgcolor="grey", font_color="white")
        # nx_network.barnes_hut()
        colors={'work':'#7dc242', 'personal':'#3e4a0b', 'research':'#fec234'}
        for path, data in dlist.items():
            label=path.split('/')[-1].rsplit('.', 1)[0]
            col='#000064'
            for j in colors:
                if j in data['folder']:
                    col=colors[j]
                    break
            nx_network.add_node(path, 
                              title=label,
                              level=2,
                              label=label, 
                              color=col, )
                              # value=v)
        for path, data in dlist.items():
            inode=nx_network.get_node(path)
            for l in data['links']:
                if l in nx_network.node_map:
                    lnode=nx_network.get_node(l)
                    nx_network.add_edge(inode['id'], lnode['id'])
        html=nx_network.generate_html('nx.html') 
        self.browser.setHtml(html)
        return html
