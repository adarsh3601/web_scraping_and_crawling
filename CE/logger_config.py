"""
File: logger_config.py
Author: Karthik Ravichandran
Date: 2024-05-25
"""

import logging


logging.basicConfig(
    filename='scraping.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    filemode='w'
)

logger = logging.getLogger()
