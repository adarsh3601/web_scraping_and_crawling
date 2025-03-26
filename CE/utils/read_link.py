
"""
File: read_link.py
Author: Karthik Ravichandran
Date: 2024-05-25
"""

import pandas as pd

def get_jobs_from_sheet1():
    job_link = pd.read_csv("./data/job_links.csv")

    return zip(tuple(job_link['Company'].tolist()), tuple(job_link['Exact Career Site Link'].tolist()))

if __name__ == '__main__':
    get_jobs_from_sheet1()
