"""
File: pipeline.py
Author: Karthik Ravichandran
Date: 2024-05-25
"""


import os
import json
import requests
from datetime import date
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from LLM_Scraper.llm_utils import HTMLParserReplicate, extract_text_content

from selenium.webdriver.common.keys import Keys

from tqdm import tqdm
import time



# support functions
def is_valid_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except:
        return False


# driver = webdriver.Chrome()

def scrape_links():
    links = []
    url = "https://dell.wd1.myworkdayjobs.com/en-US/External/?Location_Country=c4f78be1a8f14da0ab49ce1162348a5e&Location_Country=bc33aa3152ec42d4995f4791a106ed09&Location_Country=a30a87ed25634629aa6c3958aa2b91ea"
    driver.get(url)

    wait = WebDriverWait(driver, 3)

    # Get the initial height of the current page
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        updated_html = driver.page_source
        soup = BeautifulSoup(updated_html, "html.parser")

        for link in soup.find_all("a", class_="css-19uc56f"):
            href = link.get("href")
            if href and "en-US" in href:
                full_href = f"https://dell.wd1.myworkdayjobs.com{href}"
                # print(full_href)
                links.append(full_href)

        try:
            time.sleep(2)
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="next"]'))
            )
            next_button.click()
        except:
            break
    driver.close()
    return links


# Function to obtain all the details of the job taking each link from the list of links.
def scrape_job_descriptions(links, company = None, default=True):
    job_data = []

    llm_parser = HTMLParserReplicate()
    for link in tqdm(links, desc="Scraping", unit=" job"):
        try:

            response = requests.get(link)
            response2 = extract_text_content(link, default = default)
            # soup = BeautifulSoup(response.content, "html.parser")
            llm_output = llm_parser.run_parser(response2, use_cust_prompt=True)
            print(llm_output)
            job_data.append(llm_output)
        except Exception as e:
            print(e)
    # Create a pandas DataFrame with the job data
    df = pd.DataFrame(job_data)
    df.to_csv(f"out/{company}_df.csv")
    return job_data


def main():
    # function-call to store all the links from the homepage of the careers page
    job_links = scrape_links()
    # job_links = ['https://23andme.com/careers/6871069002',
    #              'https://23andme.com/careers/7314554002',
    #              'https://boards.greenhouse.io/acquia/jobs/5979236']

    # Function to generate the dataframe
    df = scrape_job_descriptions(job_links)
    print(df)
    return df

#
if __name__ == "__main__":
    main()
