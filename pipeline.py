from CE.crawler.crawler import crawler
from CE.logger_config import logger
from LLM_Scraper.llmparser import scrape_job_descriptions
from database_connection.connection import dB
import argparse
import subprocess




def get_parase_arg():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--company')
    parser.add_argument('--seed_link')
    parser.add_argument('--default', type=bool)
    return parser.parse_args()


args = get_parase_arg()
list_job = [(args.company, args.seed_link)]

search_words = ["/careers", "/jobs", "/job", "/apply", "/join-us", "/open-positions", "#openings",
                '/job-opening', '#job-opening', "boards.greenhouse.io", '/careers', 'myworkdayjobs']
# list_job = [('23andme','https://www.23andme.com/careers/jobs/')]
# list_job = [("dell", "https://dell.wd1.myworkdayjobs.com/en-US/External/?Location_Country=c4f78be1a8f14da0ab49ce1162348a5e&Location_Country=bc33aa3152ec42d4995f4791a106ed09&Location_Country=a30a87ed25634629aa6c3958aa2b91ea")]
for company, job_link in list_job:
    logger.info(f"Crawling Company => {company}")
    crawler_obj = crawler(search_words=search_words, no_level=2)
    try:
        imp_url_lvl = crawler_obj.crawler_v4(
            seed_link=job_link,company=company)
    except Exception as e:
        logger.warning(f"Exception {e} at company: {company}")

if len(imp_url_lvl)<50 and len(imp_url_lvl)>0:
    df = scrape_job_descriptions(imp_url_lvl, company=args.company, default=args.default)



# db = dB(config_path="database_connection/db_config.yaml")
# if db.db is not None:
#     # Example document to insert
#
#
#     # Insert the document into the specified collection
#
#     for i in df:
#         db.insert_document(
#             collection_name=db.config["mongo"]["collection_name"], document=i
#         )


