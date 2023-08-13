import re
import urllib.parse
import urllib.request
import fake_useragent

def translate(to_translate, to_language="auto", from_language="auto", wrap_len="80"):

    base_link = "http://translate.google.com/m?tl=%s&sl=%s&q=%s"
    to_translate = urllib.parse.quote(to_translate)
    link = base_link % (to_language, from_language, to_translate)
    ua=fake_useragent.UserAgent()
    agent={'User-Agent': str(ua.random)}
    request = urllib.request.Request(link, headers=agent)
    raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    expr = r'class="result-container">(.*?)<'
    re_result = re.findall(expr, data)
    if (len(re_result) > 0): return re_result[0]
