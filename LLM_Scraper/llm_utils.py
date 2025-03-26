"""
File: llm_utils.py
Author: Karthik Ravichandran
Date: 2024-05-25
"""

import os

from langchain_community.llms import Ollama
from CE.logger_config import logger

import os
import json
from bs4 import BeautifulSoup
from langchain.chains import SimpleSequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import re
import json
import requests
import replicate
import yaml
import os

root_dir = os.path.dirname(os.path.abspath(__file__))
config_path = "CrawlingAndScraping/LLM_Scraper/llm_config.yaml"
config_path = "LLM_Scraper/llm_config.yaml"

class promptLlm:
    def __init__(self):
        self.__load_base_config__()
        self.__init_default_prompt__()

    def __init_default_prompt__(self):
        self.base_prompt = '''parse this html and put it in json -> (job_id, date_posted, company_name, job_title, job_type, Description summary ,
location, country, source_link, apply_link) just give me the final json for these fileds , dont give python code
'''
        self.suffix_prompt = '''Convert this json format as follows '''

        self.json_prompt = '''{"job_id": ,
                            "date_posted": ,
                            "company_name": ,
                            "job_title": ,
                            "job_type": ,
                            "description_summary": only 30 words ,
                            "location": ,
                            "country": ,
                            "source_link": ,
                            "apply_link": 
                            }'''
        self.rule_prompt = '''put the json in inside this <start_json> json data <end_json>'''


    def __load_base_config__(self):
        print(os.listdir())
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def load_config(self, provider = 'replicate'):
        if provider == 'replicate':
            self.load_replicate_config()


    def load_replicate_config(self):

        os.environ["REPLICATE_API_TOKEN"] = self.config["configurations"]\
            ["api_config"]["replicate_api_key"]
        self.input_config = self.config["configurations"]['llm_config']["input"]
        self.model_name = self.config["configurations"]["llm_config"]['model']
        self.cust_prompt = self.config["configurations"]["custom_prompt"][0]


class llmParser:
    def __init__(self, model="llama3"):
        self.model = model
        self.llm = Ollama(model=self.model)
        self.llm_test()
        self.init_parse_command()

    def llm_test(self):
        try:
            outcome = self.llm.invoke("Tell me a joke")
            if len(outcome)>5:
                logger.info(f"Ollama server running with LLM {self.model}")
            else:
                logger.warning(f"LLM is running but output has an issue!!!")
        except:
            logger.warning(f"LLM not running: Ollama or model issue!!!")

    def init_parse_command(self):
        self.base_prompt = ''' Parse following information from html file (Dont give any code just parse: '''
        self.info_prompt = '''
                job_id, date_posted, company_name, job_title, job_type, Description,
                 location, country, source_link, apply_link'''
        self.json_prompt = '''Format the output into to the dict format with respective keywords fields 
                        and put NULL is the information is not aviable '''

    def get_prompt(self, html_str):
        self.final_prompt = f"{self.base_prompt} '''{html_str}''' {self.info_prompt} and {self.json_prompt}"
        return f'''parse this and put it in json -> (job_id, date_posted, company_name, job_title, job_type, Description,
                 location, country, source_link, apply_link) just give me the final json for these fileds , dont give python code

                HTML : {html_str}'''

    def get_prompt_json(self, out):

        return f"""Convert this text into json\n TEXT: {out}"""
        # return self.final_prompt

    def run_llm(self, html_str):
        out = self.llm.invoke(self.get_prompt(html_str))
        out = self.llm.invoke(self.get_prompt(out))
        return out
class HTMLParserChain:
    def __init__(self):
        self.llm = OpenAI()  # specify your model

    def parse_html(self, html_content: str) -> dict:
        soup = BeautifulSoup(html_content, 'html.parser')

        job_data = {}

        script_tag = soup.find('script', type='application/ld+json')
        job_json = json.loads(script_tag.string)

        job_data['job_id'] = job_json['identifier']['value']
        job_data['date_posted'] = job_json['datePosted']
        job_data['company_name'] = job_json['hiringOrganization']['name']
        job_data['job_title'] = job_json['title']
        job_data['job_type'] = job_json['employmentType']
        job_data['Description'] = job_json['description']
        job_data['location'] = job_json['jobLocation']['address']['addressLocality']
        job_data['country'] = job_json['jobLocation']['address']['addressCountry']
        job_data['source_link'] = soup.find('link', rel='canonical')['href']
        job_data['apply_link'] = job_json['url']

        return job_data

    def call_openai(self, html_content: str) -> dict:
        html_content = None
        prompt = (
            "Extract the following details from the provided HTML content:\n"
            "job_id, date_posted, company_name, job_title, job_type, Description, "
            "location, country, source_link, apply_link.\n\n"
            f"HTML content:\n{html_content}\n\n"
            "Extracted details in JSON format:"
        )

        response = self.llm(prompt)
        return json.loads(response)
class HTMLParserReplicate(promptLlm):
    def __init__(self):
        super(HTMLParserReplicate, self).__init__()
        self.load_config(provider='replicate')

    def __default_prompt__(self, html_page):
        self.prompt = (f"{self.base_prompt} \n HTML: {html_page} \n {self.suffix_prompt}"
                       f" {self.json_prompt} \n {self.rule_prompt}")
        return self.prompt

    def __custom_prompt__(self, html_page):
        self.prompt = (f"{self.cust_prompt['base_prompt']} "
                       f"\n HTML: {html_page} "
                       f"\n {self.cust_prompt['json_prompt']} "
                       f"\n {self.cust_prompt['suffix_prompt']} "
                       f"\n {self.cust_prompt['rule_prompt']}")
        return self.prompt

    def run_llm(self):
        if self.use_cust_prompt:
            prompt = self.__custom_prompt__(self.html_page)
        else:
            prompt = self.__default_prompt__(self.html_page)


        final_output = []
        for event in replicate.stream(
            self.model_name,
           # "meta/meta-llama-3-8b-instruct",
           input={
               "top_k": self.input_config['top_k'],
               "top_p": self.input_config['top_p'],
               "prompt": prompt,
               "temperature": self.input_config['temperature'],
               "length_penalty": self.input_config['length_penalty'],
               "max_new_tokens": self.input_config['max_new_tokens'],
               "prompt_template": self.input_config['prompt_template'],
               "presence_penalty": self.input_config['presence_penalty'],
           },
       ):
            final_output.append(str(event))
        final_output = "".join(final_output)
        return final_output


    def run_parser(self, html_page, use_cust_prompt=False):
        self.html_page = html_page
        self.use_cust_prompt = use_cust_prompt
        parsed_data = self.run_llm()

        regex = r"<start_json>(.*?)<end_json>"
        
        # Find the match in the sample string
        match = re.search(regex, parsed_data, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            json_data = json.loads(json_str)

        return json_data


def extract_text_content(url, default=True):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')


    if not default:
    # Combine all text within <p> tags
        paragraphs = soup.find_all('p')
        text_content = ' '.join([p.get_text() for p in paragraphs])

        # Additional extraction from headings if needed
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        heading_content = ' '.join([h.get_text() for h in headings])

        # Combine paragraph and heading content
        full_text_content = heading_content + ' ' + text_content
        logger.info("HTML Full =====>")
        logger.info(full_text_content)
        logger.info("HTML End  xxxxxx")
    else:
        full_text_content = str(soup)

    return full_text_content


# Example usage
if __name__ == "__main__":
    html_content = '''<!DOCTYPE html>

<html lang="en-US">
<head>
<title></title>
<!-- Application Properties -->
<meta content="chrome=1;IE=EDGE" http-equiv="X-UA-Compatible"/>
<meta content="text/html; charset=utf-8" http-equiv="content-type"/>
<meta content="width=device-width, initial-scale=1.0, maximum-scale=2.0" name="viewport"/>
<link href="https://dell.wd1.myworkdayjobs.com/en-US/External/job/Internal-Audit-SOX-Senior-Advisor_R246118" rel="canonical"/>
<!-- OpenGraph Tags -->
<meta content="Internal Audit SOX Senior Advisor" name="title" property="og:title"/>
<meta content="Internal Audit SOX Senior Advisor We’re a global business – a multi-billion-dollar corporation. To stay strong and secure, it’s vital to have a robust audit and risk assessment of our financial and operational practices. That’s where our Internal Audit professionals come in. Preparing independent audit plans, conducting internal reviews and establishing audit criteria, they ensure full compliance with legislatively mandated initiatives including Sarbanes-Oxley. Auditing the activities of diverse departments, reporting the results to leadership and the Audit committee – and recommending controls if appropriate – this dedicated team makes sure that our organization is a fully compliant success. Join us to do the best work of your career and make a profound social impact as an Internal Audit Senior Advisor (SOX Audit) on our Global Audit Transformation (GAT) Sarbanes Oxley (SOX) team in Round Rock, Texas or Hopkinton, Massachusetts. What you’ll achieve As Internal Audit Senior Advisor you will function as critical point of contact with business unit process and control owners, and other stakeholders to ensure that process and assessment documentation is current and accurate. You will support major system implementations such as 1Finance, SailPoint etc and partner with business and other stakeholders to embed effective controls from a SOX perspective. You will also lead process walkthroughs of coverage areas with business units and external audit staff and coordinate and perform controls testing and review. You will: Act as a point of contact to external audit staff ensuring timely delivery of work papers and supporting testing evidence Support the GAT SOX team through effective administration of Archer and SharePoint for the documentation and completion of test records, workpapers, and status reporting functionality Assist GAT SOX management with ad hoc projects across organizational and functional boundaries Participate in the development of the annual SOX assurance plan, scoping and year-end activities as well as the creation of real-time SOX operational reporting dashboards Explore use cases and developing/adopting tools or methods that make use of generative AI, bots, or existing technology to help with control testing automation and process improvements Take the first step towards your dream career Every Dell Technologies team member brings something unique to the table. Here’s what we are looking for with this role: Essential Requirements Bachelor’s degree with 8+ years of professional experience Audit/SOX background and experience in managing SOX projects with a keen sense of professional skepticism and a questioning/analytical mind including driving process optimization Knowledge of SOX controls, conducting walkthroughs and testing experience in an internal/external audit or business unit capacity Understanding of IT related business controls such as Segregation of Duties, User Access, Interfaces, SOC-1 Reports and Key Reports Working knowledge of Archer is a plus Desirable Requirements An audit certification (at least partial completion) such as CIA, is preferable Working knowledge of technologies utilized for process improvements, analytics and automation Who we are We believe that each of us has the power to make an impact. That’s why we put our team members at the center of everything we do. If you’re looking for an opportunity to grow your career with some of the best minds and most advanced tech in the industry, we’re looking for you. Dell Technologies is a unique family of businesses that helps individuals and organizations transform how they work, live and play. Join us to build a future that works for everyone because Progress Takes All of Us. Application closing date: 07 June 2024 Dell Technologies is committed to the principle of equal employment opportunity for all employees and to providing employees with a work environment free of discrimination and harassment. Read the full Equal Employment Opportunity Policy here. #LI-Hybrid Dell Technologies helps organizations and individuals build their digital future and transform how they work, live and play. The company provides customers with the industry’s broadest and most innovative technology and services portfolio for the data era." name="description" property="og:description"/>
<meta content="https://dell.wd1.myworkdayjobs.com/en-US/External/assets/logo" name="image" property="og:image"/>
<meta content="website" property="og:type"/>
<meta content="https://dell.wd1.myworkdayjobs.com/en-US/External/job/Round-Rock-Texas-United-States/Internal-Audit-SOX-Senior-Advisor_R246118" property="og:url"/>
<!-- SEO Tags -->
<script type="application/ld+json">
        {
  "jobLocation" : {
    "@type" : "Place",
    "address" : {
      "@type" : "PostalAddress",
      "addressCountry" : "United States of America",
      "addressLocality" : "Round Rock, Texas, United States"
    }
  },
  "applicantLocationRequirements" : {
    "@type" : "Country",
    "name" : "United States of America"
  },
  "jobLocationType" : "TELECOMMUTE",
  "hiringOrganization" : {
    "name" : "DELL USA L.P. (1001)",
    "@type" : "Organization",
    "sameAs" : ""
  },
  "identifier" : {
    "name" : "Internal Audit SOX Senior Advisor",
    "@type" : "PropertyValue",
    "value" : "R246118"
  },
  "datePosted" : "2024-05-22",
  "employmentType" : "FULL_TIME",
  "title" : "Internal Audit SOX Senior Advisor",
  "description" : "Internal Audit SOX Senior Advisor We’re a global business – a multi-billion-dollar corporation. To stay strong and secure, it’s vital to have a robust audit and risk assessment of our financial and operational practices. That’s where our Internal Audit professionals come in. Preparing independent audit plans, conducting internal reviews and establishing audit criteria, they ensure full compliance with legislatively mandated initiatives including Sarbanes-Oxley. Auditing the activities of diverse departments, reporting the results to leadership and the Audit committee – and recommending controls if appropriate – this dedicated team makes sure that our organization is a fully compliant success. Join us to do the best work of your career and make a profound social impact as an Internal Audit Senior Advisor (SOX Audit) on our Global Audit Transformation (GAT) Sarbanes Oxley (SOX) team in Round Rock, Texas or Hopkinton, Massachusetts. What you’ll achieve As Internal Audit Senior Advisor you will function as critical point of contact with business unit process and control owners, and other stakeholders to ensure that process and assessment documentation is current and accurate. You will support major system implementations such as 1Finance, SailPoint etc and partner with business and other stakeholders to embed effective controls from a SOX perspective. You will also lead process walkthroughs of coverage areas with business units and external audit staff and coordinate and perform controls testing and review. You will: Act as a point of contact to external audit staff ensuring timely delivery of work papers and supporting testing evidence Support the GAT SOX team through effective administration of Archer and SharePoint for the documentation and completion of test records, workpapers, and status reporting functionality Assist GAT SOX management with ad hoc projects across organizational and functional boundaries Participate in the development of the annual SOX assurance plan, scoping and year-end activities as well as the creation of real-time SOX operational reporting dashboards Explore use cases and developing/adopting tools or methods that make use of generative AI, bots, or existing technology to help with control testing automation and process improvements Take the first step towards your dream career Every Dell Technologies team member brings something unique to the table. Here’s what we are looking for with this role: Essential Requirements Bachelor’s degree with 8+ years of professional experience Audit/SOX background and experience in managing SOX projects with a keen sense of professional skepticism and a questioning/analytical mind including driving process optimization Knowledge of SOX controls, conducting walkthroughs and testing experience in an internal/external audit or business unit capacity Understanding of IT related business controls such as Segregation of Duties, User Access, Interfaces, SOC-1 Reports and Key Reports Working knowledge of Archer is a plus Desirable Requirements An audit certification (at least partial completion) such as CIA, is preferable Working knowledge of technologies utilized for process improvements, analytics and automation Who we are We believe that each of us has the power to make an impact. That’s why we put our team members at the center of everything we do. If you’re looking for an opportunity to grow your career with some of the best minds and most advanced tech in the industry, we’re looking for you. Dell Technologies is a unique family of businesses that helps individuals and organizations transform how they work, live and play. Join us to build a future that works for everyone because Progress Takes All of Us. Application closing date: 07 June 2024 Dell Technologies is committed to the principle of equal employment opportunity for all employees and to providing employees with a work environment free of discrimination and harassment. Read the full Equal Employment Opportunity Policy here. #LI-Hybrid Dell Technologies helps organizations and individuals build their digital future and transform how they work, live and play. The company provides customers with the industry’s broadest and most innovative technology and services portfolio for the data era.",
  "@context" : "http://schema.org",
  "@type" : "JobPosting"
}
    </script>
<script type="text/javascript">
        window.workday = window.workday || {
            tenant: "dell",
            siteId: "External",
            locale: "en-US",
            requestLocale: "en-US",
            supportedLocales:["de-DE","en-US","es","fr-CA","fr-FR","pt-BR","ja-JP","zh-CN"],
            clientOrigin: "https://www.myworkday.com",
            language: null,
            cdnEndpoint: "www.myworkdaycdn.com",
            useCdn: true,
            maintenancePageUrl: "https://www.myworkday.com/wday/drs/outage?t=dell&s=External",
            token: "561d6c29-d225-4fbc-844b-682b5ce8516b",
            environment: "PROD",
            isExternal: true,
            postingAvailable: true,
            allowedFileTypes: [],
            blockedFileTypes: []
        };
        function createScriptTag (src) {
            var scriptTag =  document.createElement('script');
            scriptTag.src = src;
            scriptTag.setAttribute('defer', 'true');
            return scriptTag;
        }
        var isIE = typeof Symbol === 'undefined';
        var sharedAssetPath = '/wday/asset/uic-shared-vendors';
        var sharedVendorLoaderAsset = sharedAssetPath + '/shared-vendors.min.js';
        var cdnOrigin = 'https://' + "www.myworkdaycdn.com";
        var sharedVendorsLoaderUrlOrigin = workday.clientOrigin !== '' ? workday.clientOrigin : cdnOrigin;
        var sharedVendorsLoaderScript = createScriptTag(sharedVendorsLoaderUrlOrigin + sharedVendorLoaderAsset);
        sharedVendorsLoaderScript.onload = function () {
            var jobsScriptSrcFilename = isIE
                ? 'cx-jobs-ie.min.js'
                : 'cx-jobs.min.js';
            var cxJobsAsset = '/wday/asset/candidate-experience-jobs/' + jobsScriptSrcFilename;
            var jobsScript = createScriptTag(cdnOrigin + cxJobsAsset);
            jobsScript.onerror = function () {
                window.workday.useCdn = false;
                var jobsScriptFromClientOrigin = createScriptTag(workday.clientOrigin + cxJobsAsset);
                document.head.removeChild(jobsScript);
                document.head.appendChild(jobsScriptFromClientOrigin);
            }
            document.head.appendChild(jobsScript);
        };
        document.head.appendChild(sharedVendorsLoaderScript);

        var uxInsightsAssetPath = '/wday/asset/client-analytics';
        var uxInsightsAsset = uxInsightsAssetPath + "/uxInsights.min.js?plate=BMT216A"
        var uxInsightsUrlOrigin = workday.clientOrigin !== '' ? workday.clientOrigin : cdnOrigin;
        var uxInsightsScript = createScriptTag(uxInsightsUrlOrigin + uxInsightsAsset);
        document.head.appendChild(uxInsightsScript);
    </script>
</head>
<body>
<div id="root"></div>
</body>
</html>'''
    # parser = HTMLParserChain()
    parser = HTMLParserReplicate()

    parsed_data = parser.run_parser(html_content, use_cust_prompt=True)

    print(parsed_data)
