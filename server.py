 #!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line
import json
import requests
from bs4 import BeautifulSoup
from datetime import date
from test_soup import TEST_SOUP

define("port", default=8080, help="run on the given port", type=int)

TEST = True
url = "http://www.operationworld.org/country/%s/owtext.html"

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
    	country = self.get_argument("country", None)

    	if TEST:
    		ow_raw = TEST_SOUP
    	else:
    		r = requests.get(url % country)
    		ow_raw = r.text

    	ow_soup = BeautifulSoup(ow_raw)

    	text = ow_soup.find('div', {'id':"cou_text"})
        tags = text.find_all(['h3', 'p'])

        section = None
        ow_dict = {
            'country_name': str(ow_soup.title.get_text().replace(" | Operation World", "")),
            'url': url % country,
            'geography': {'other':[]},
            'people': {'other':[]},
            'religion': {'other':[]},
            'prayer_answers': [],
            'prayer_challenges': [],
            'copyright': "All content copyright Operation World. For more information visit the OW website (operationworld.org). Data retrieved: %s." % date.today()
        }

        for t in tags:

            if t.name == 'h3':
                section = self.id_section(t.text)

            if t.name == 'p' and section is not None:
                if section not in ['geography', 'people', 'religion']:
                    ow_dict[section].append(t.text.strip())
                else:
                    text = self.parse_paragraph(t.text)
                    if type(text) is list:
                        ow_dict[section][text[0]] = text[1]
                    else:
                        ow_dict[section]['other'].append(text)



    	ow_json = json.dumps(ow_dict)
    	self.add_header('Content-Type', 'application/json')
    	self.write(ow_json)

    def id_section(self, section_name):

        if section_name == 'Geography':
            return 'geography'

        if section_name == 'Peoples':
            return 'people'

        if section_name == 'Religion':
            return 'religion'

        if section_name == 'Answers to Prayer':
            return 'prayer_challenges'

        if section_name == 'Challenges for Prayer':
            return 'prayer_challenges'

        return None

    def parse_paragraph(self, paragraph):

        if ':' in paragraph:
            para_split = paragraph.split(':', 1)
            para_split[1] = para_split[1].strip()
            return para_split
        else:
            return paragraph

        

app = tornado.web.Application([
    (r'/', IndexHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()