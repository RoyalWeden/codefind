from app import config
import uuid
import requests
from app.routes import sqldb

class CustomSearch():
    def __init__(self):
        self.api_key = config['GOOGLE_CUSTOM_SEARCH_API_KEY']
        self.engine_id = config['GOOGLE_PROGRAMMABLE_SEACH_ENGINE_ID']

    def get_searches(self, query):
        api_url = "https://www.googleapis.com/customsearch/v1?key={0}&cx={1}".format(self.api_key, self.engine_id)
        search_params = {
            'q': query,
            'dateRestrict': "",
            'exactTerms': "",
            'excludeTerms': "",
            'num': 10,
            'orTerms': "",
            'relatedSite': "",
            'siteSearch': ""
        }
        for key in search_params:
            if search_params[key] != '':
                api_url += "&{0}={1}".format(key, search_params[key])

        r = requests.get(api_url)
        search_items = []

        for item in r.json()['items']:
            title = str(item['title']).replace('\'', '')
            description = str(item['snippet']).replace('\n', '').replace('\xa0', '').replace('\'', '')
            link = str(item['link'])
            domain = str(item['displayLink'])
            id = str(uuid.uuid3(uuid.NAMESPACE_URL, link))
            search_item = {
                'id': id,
                'title': title,
                'description': description,
                'link': link,
                'domain': domain
            }
            search_items.append(search_item)
            sqldb.create_source(search_item)

        # print(search_items)
        return search_items
        
