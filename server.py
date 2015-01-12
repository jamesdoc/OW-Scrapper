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

    	ow_dict = {
    		'country_name': str(ow_soup.title.get_text().replace(" | Operation World", "")),
    		'url': url % country,
    		'geography': {},
    		'people': {},
    		'religion': {},
    		'prayer_answers': {},
    		'prayer_challenges': {},
    		'copyright': "All content copyright Operation World. For more information visit the OW website (operationworld.org). Data retrieved: %s." % date.today()

    	}

    	ow_json = json.dumps(ow_dict)
    	self.add_header('Content-Type', 'application/json')
    	self.write(ow_json)

app = tornado.web.Application([
    (r'/', IndexHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()