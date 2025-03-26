
"""
File: crawler.py
Author: Karthik Ravichandran
Date: 2024-05-25
"""

import requests
from bs4 import BeautifulSoup
import queue
from tqdm import tqdm
from CE.crawler.url_logic import urlLogic
from CE.logger_config import logger
from CE.utils.job_descriptor import *
# from selenium import webdriver
from urllib.parse import urljoin

def parse_level_one_urls(url,base_url,search_words):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        }
    url = f"{url}?page=1"
    response = requests.get(url,headers=headers)
    if response.status_code!=200:
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    links = [urljoin(base_url,x.get('href')) for x in soup.find_all('a') if x.get('href')]
    job_links = []
    for link in links:
        inserted = False
        for i,job_link in enumerate(job_links):
            if len(job_link)>0 and check_job_descriptors(job_link[0],link):
                job_links[i].append(link)
                inserted = True
        if not inserted:
            job_links.append([link])
    
    job_link = ''
    urls = []
    for i in job_links:
        if any(all(word in sentence for sentence in i) for word in search_words):
            if len(i) > len(urls):
                urls = i
                job_link = i[0]
    
    return job_link, urls

class crawler:

    def __init__(self, search_words, search_positions=None, no_level = 2):
        self.search_words = search_words
        self.no_level = no_level
        self.search_positions = search_positions


    def crawler_v1(self, seed_link, company):
        if 'https://' not in seed_link:
            seed_link = "https://" + seed_link
        urllogic = urlLogic()
        base_url = seed_link
        # search_words.append('jobs')
        urls = queue.PriorityQueue()
        urls.put((0.5, seed_link))
        visited_urls = []
        imp_url_lvl = {}
        # until all pages have been visited
        for level in tqdm(range(self.no_level)):
            imp_urls = []
            # get the page to visit from the list
            try:
                _, current_url = urls.get(timeout=4)
            except :
                logger.warning(f'Exception: {str(urls)}')
                # print(f'Exception: {str(urls)}')


            # crawling logic
            response = requests.get(current_url)
            soup = BeautifulSoup(response.content, "html.parser")
            visited_urls.append(current_url)
            link_elements = soup.select("a[href]")
            link_elements = [link_element["href"] for link_element in link_elements]
            for link_element in link_elements:
                url = link_element
                # url = link_element["href"]
                check_url = False
                for i in self.search_words: #
                    if i in url:
                        check_url = True

                if check_url:
                    # if the URL discovered is new
                    if url not in visited_urls and url not in [
                        item[1] for item in urls.queue
                    ]:
                        # low priority
                        priority_score = 1
                        # if it is a pagination page
                        if "http" not in url:
                            url = urllogic.test_url_logic(base_url, url)
                            # url = f"{base_url}/{url.split('/')[-2]}"
                        add_url = False
                        if self.search_positions:
                            for i in self.search_words:
                                if i in url:
                                    add_url = True
                        else:
                            add_url = True
                        if add_url:
                            # high priority
                            priority_score = 0.5
                            imp_urls.append(url)
                            # print(f"At Level: {level} -> Url: {url}")
                            logger.info(f"At Level: {level} -> Url: {url}")
                        urls.put((priority_score, url))
            imp_url_lvl[level] = list(set(imp_urls))
        return imp_url_lvl

    def crawler_v2(self, seed_link):
        if "https://" not in seed_link:
            seed_link = "https://" + seed_link

        urllogic = urlLogic()
        urls = queue.PriorityQueue()
        urls.put((0.5, seed_link))
        visited_urls = set()
        imp_url_lvl = {}

        for level in tqdm(range(self.no_level)):
            imp_urls = []

            try:
                _, current_url = urls.get(timeout=4)
            except queue.Empty:
                logger.warning(f"Exception: {str(urls)}")
                break

            response = requests.get(current_url)
            soup = BeautifulSoup(response.content, "html.parser")
            visited_urls.add(current_url)

            link_elements = [link.get("href") for link in soup.select("a[href]")]
            for url in link_elements:
                if not url.startswith("http"):
                    url = urllogic.test_url_logic(seed_link, url)

                if any(word in url for word in self.search_words) and url not in visited_urls:
                    priority_score = 0.5 if any(word in url for word in self.search_words) else 1
                    urls.put((priority_score, url))
                    if priority_score == 0.5:
                        if url in imp_urls:
                            continue
                        imp_urls.append(url)
                        logger.info(f"At Level: {level} -> Url: {url}")

            imp_url_lvl[level] = list(set(imp_urls))

        return imp_url_lvl

    def crawler_v3(self,seed_link,company):
        logger.info(f"Starting crawling for {company}")
        if 'https://' not in seed_link:
            seed_link = "https://" + seed_link
        base_url = '/'.join(seed_link.split('/', 3)[:3])
        logger.info(f"Base URL: {base_url}")

        urls = queue.PriorityQueue()
        urls.put((0, seed_link))  # Highest priority for the seed link
        visited_urls = set()
        queue_membership = set()
        top_level = None
        job_description_url = None
        url_logic = urlLogic()

        crawled_urls = {}

        # device = webdriver.Chrome()
        
        while not urls.empty():
            try:
                priority, current_url = urls.get()
                
                current_priority_urls = crawled_urls.get(priority,[])
                if current_url not in current_priority_urls:
                    crawled_urls[priority] = crawled_urls.get(priority,[])+[current_url]
                if top_level and priority == top_level:
                    # print(priority, current_url, 'job url')
                    urls.put((priority,current_url))
                    break
                if current_url in visited_urls or priority==4:
                    continue  # Skip if already visited
                visited_urls.add(current_url)
                logger.info(f"Visiting: {current_url} priority {priority}")
                device.get(current_url)
                soup = BeautifulSoup(device.page_source, "html.parser")
                if priority>0 and is_job_description_page(soup):
                    top_level = priority
                    job_description_url = current_url
                    urls.put((priority,current_url))
                    continue
                link_elements = list(set([link.get("href") for link in soup.select("a[href]")]))

                for url in link_elements:   
                
                    try:
                        if (url=='/') or  (not url.startswith('/') and not url.startswith('http') \
                            and not url.startswith('#')) or ('xml' in url) :
                            continue
                        
                        if url.startswith('#'):
                            urls_ = [current_url+url]
                            # print(urls_,url,"satrtswirh#")
                        elif "http" not in url:
                            urls_ = url_logic.test_url_logic('/'.join(current_url.split('/', 3)[:3]), url)
                        else:
                            urls_ = [url]
                        if len(urls_)==0:
                            continue
                        for url in urls_:
                            if url not in visited_urls and any(word in url for word in self.search_words):
                                priority_score = priority+1
                                if (priority_score,url) not in queue_membership and priority_score<5 and ("linkedin" not in url):
                                    urls.put((priority_score, url))
                                    queue_membership.add((priority_score,url))
                            
                    except Exception as e:
                        continue
                
                    # return
            except Exception as e:
                # print(current_url)
                # logger.warning(f'Exception "{e}" occured url {current_url} at')
                continue

        try:
            while not urls.empty():
                priority,url = urls.get()
                if check_job_descriptors(job_description_url,url) and priority==top_level:
                    if ("linkedin" not in url or "instagram" not in url):
                        logger.info(f"At Level: {priority} -> Url: {url}")
                if priority==top_level:
                    crawled_urls[priority] = crawled_urls.get(priority,[])+[url]
            if not top_level:
                print("not in queue123")
                for link in crawled_urls[max(list(crawled_urls.keys()))]:
                    if ("linkedin" not in url or "instagram" not in link):
                        logger.info(f"At Level: {max(list(crawled_urls.keys()))} -> Url: {link}")
        except Exception as e:
            logger.warning(f"Exception {e} occured while populating urls")
        # print(list(set(crawled_urls[top_level])))
        logger.info(f"Completed crawling for {company}")

    def crawler_v4(self,seed_link,company):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        }
        job_urls = []

        try:
            job_url, urls = parse_level_one_urls(seed_link, seed_link,self.search_words)
        except Exception as e:
            job_url, urls = '',[]
            print(e)
        job_urls += urls
        for page in range(2,300):
            # break
            try:
                url = f"{seed_link}?page={page}"
                response = requests.get(url, timeout=15, headers=headers)
                if response.status_code!=200:
                    break
                soup = BeautifulSoup(response.content, 'html.parser')
                new_links = [x.get('href') for x in soup.find_all('a') if x.get('href')]
                # print(new_links,"newlinks123")
                new_links = [urljoin(seed_link,x) if not x.startswith('http') else x for x in new_links]
                new_links = [x for x in new_links if x not in job_urls and check_job_descriptors(job_url,x)]
                
                if len(new_links)==0:
                    break
                # print(len(job_urls))
                job_urls += new_links
            except Exception as e:
                print(f'Exception {e} occured for page {page}')
        print(f'Scraped {len(job_urls)} links for {company}')
        logger.info(f'Scraping for company {company} started')
        for url in job_urls:
            try:
                logger.info(url)
            except Exception as e:
                print(e)
        logger.info(f'Scraping for company {company} completed')
        return job_urls


if __name__=='__main__':
    seed_link = 'https://www.acquia.com/careers'
    seed_link = "https://www.23andme.com/careers"

    imp_url_lvl = crawler().crawler_v4(seed_link=seed_link,
                             search_words=['/jobs', '/join-us', '/open-positions', "#openings"],
                             no_level=3)

    print(imp_url_lvl)