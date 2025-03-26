"""
File: logger_config.py
Author: Karthik Ravichandran
Date: 2024-05-25
"""


import logging


logging.basicConfig(
    filename='llm_scraping.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',

)

logger = logging.getLogger()
