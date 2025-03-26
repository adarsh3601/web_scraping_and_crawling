"""
File: pipeline.py
Author: Karthik Ravichandran
Date: 2024-05-25
"""
from utils.read_link import get_jobs_from_sheet1
from crawler.crawler import crawler
from logger_config import logger

if __name__ == '__main__':
    search_words = ["/careers", "/jobs", "/job", "/apply", "/join-us", "/open-positions", "#openings", 
                    '/job-opening', '#job-opening', "boards.greenhouse.io", '/careers', 'myworkdayjobs']
    list_job = get_jobs_from_sheet1()
    list_job = [('23andme','https://www.23andme.com/careers/jobs/')]
    # list_job = [("dell", "https://dell.wd1.myworkdayjobs.com/en-US/External/?Location_Country=c4f78be1a8f14da0ab49ce1162348a5e&Location_Country=bc33aa3152ec42d4995f4791a106ed09&Location_Country=a30a87ed25634629aa6c3958aa2b91ea")]
    for company, job_link in list_job:
        logger.info(f"Crawling Company => {company}")
        crawler_obj = crawler(search_words=search_words, no_level=2)
        try:
            imp_url_lvl = crawler_obj.crawler_v4(
                seed_link=job_link,company=company)
        except Exception as e:
            logger.warning(f"Exception {e} at company: {company}")

