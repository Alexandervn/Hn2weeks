#!/usr/bin/env python

import os
import urllib2
import simplejson as json
from datetime import *
import time
import calendar
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from dateutil.relativedelta import *

class MainHandler(webapp.RequestHandler):

    def get(self):
        template_values = {'results': [], 'dates': []}

        day_of_month = int(time.strftime('%d'))
        today = date.today()

        # 1st half of month: choose 2nd half of previous month
        if (day_of_month < 15):
            from_date = today + relativedelta(day=15, months=-1)
            last_day_of_previous_month = calendar.monthrange(today.year, today.month)[1]
            to_date = today + relativedelta(day=last_day_of_previous_month, months=-1)
            next_update = today + relativedelta(day=15) 

        # 2nd half of month: choose 1st half of this month
        else:
            from_date = today + relativedelta(day=1)
            to_date = today + relativedelta(day=14)
            next_update = today + relativedelta(day=1, months=+1) 

        from_date = from_date.strftime('%Y-%m-%d');
        to_date = to_date.strftime('%Y-%m-%d');
        next_update = next_update.strftime('%Y-%m-%d');

        template_values['dates'] = {
                'from_date': from_date, 
                'to_date': to_date, 
                'next_update': next_update
        }

        url = "http://api.thriftdb.com/api.hnsearch.com/items/_search?sortby=num_comments%20desc&filter[fields][create_ts]=[" + from_date  + "T00:00:00Z%20TO%20" + to_date  + "T23:59:59Z]&filter[fields][type]=submission&pretty_print=true&limit=35"

        try:
            f = urllib2.urlopen(url)
            results = json.load(f)['results']
        except urllib2.URLError, e:
            self.response.out.write('Could not load results!')

        if ('results' in locals()):
            for result in results:
                item = result['item']
                item['create_ts'] = datetime.strptime(item['create_ts'], '%Y-%m-%dT%H:%M:%SZ')
                template_values['results'].append(item)

            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values).decode('utf-8'))


def main():
    application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
