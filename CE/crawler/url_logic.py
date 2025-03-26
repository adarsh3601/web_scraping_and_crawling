"""
File: url_logic.py
Author: Karthik Ravichandran
Date: 2024-05-25
"""

import requests
class urlLogic:
    def __init__(self):
        self.base_url = None
        self.url = None
        self.set_of_func = [self.logic4, self.logic1, self.logic2, 
                            self.logic3, self.logic5]
        self.found_logic = []

    def logic1(self, base_url, url):
        # print(f"{base_url} {url} logic {url.split('/')[:-2]}")
        return f"{base_url}{'/'.join(url.split('/')[:-2])}"

    def logic2(self, base_url, url):
        return f"{base_url}{url}"

    def logic3(self, base_url, url):
        return f"{url}"

    def logic4(self, base_url, url):
        base_url = "/".join(base_url.split("/")[:-1])
        return f"{base_url}{url}"

    def logic5(self, base_url, url):
        return f"{base_url}/{url.split('/')[-2]}"

    def get_logicfn(self, base_url, url):
        return [fn(base_url, url) for fn in self.set_of_func]

    def get_valid_urls(self,logics,base_url,url):
        urls = []
        for logic in logics:
            urls.append(self.set_of_func[logic](base_url, url))
        return urls

    def test_url_logic(self, base_url, url):
        # print("test logic ", base_url, url)
        if len(self.found_logic)>0:
            # return self.set_of_func[self.found_logic](base_url, url)
            return self.get_valid_urls(self.found_logic,base_url,url)
        valid_urls = []
        urls = self.get_logicfn(base_url, url)
        for logic, url in enumerate(urls):
            # print(logic, url, "inside test logic")
            if url[:-1] == base_url:
                continue
            try:
                response = requests.get(url)
            except Exception as e:
                # print(f'Exception {e} from test logic')
                continue

            if response.status_code == 200:
                self.found_logic.append(logic)
                # print("return from test logic with url", logic)
                valid_urls.append(url)
        # print("return from test logic with none")
        # print(self.found_logic, valid_urls,"valid urls123")
        return valid_urls