
# Job Scraper and Crawling Engine


## Getting Started 
1) Clone the Repo and checkout to `Karthik-CE` branch
2) Make a conda env and install the packages mentioned in `requirments.txt` (check the CE directory for the file)
3) Try running `run.py` and you should be able to generate csvs in `out` dir



## Overview

This project addresses the problem of extracting job listings from various sources. We propose two solutions:

1. **Short-term solution**: Writing a web scraper for specific URLs.
2. **Long-term solution**: Developing a crawling engine combined with a scraper to gather job listings from multiple job search portals.

## Solutions

### Case 1: Short-term Solution

In the short-term solution, we focus on writing a web scraper to extract information from a given URL.

- **Implementation**: 
  - The scraper method will vary based on the URL.
  - Requires the specific URL of the job portal to proceed with implementation.

- **Challenges**:
  - Obtaining URLs for all job portals.
  - Scalability: Writing individual scrapers for each company is impractical. Managing scrapers for 10 companies is feasible, but scaling to 2000 or more is not.

### Case 2: Long-term Solution

In the long-term solution, we design a comprehensive crawling engine that can discover job listings from various job search portals (e.g., LinkedIn, Indeed, and other job search engines).

- **Implementation**:
  - The crawling engine will search for URLs on job portals rather than individual company career sites.
  - Once URLs are fetched, the engine will scrape the required job listing information.
  - A general scraper will be defined with the help of Local Large Language Models (LLMs) to adapt to different job portals.

- **Challenges**:
  - Requires more development effort and research.
  - Designing a flexible and robust solution to handle various formats and portals.

## Conclusion

Choosing between the short-term and long-term solutions depends on the project's immediate needs and scalability requirements. The short-term solution offers a quick implementation but is limited in scope and scalability. The long-term solution, although requiring more initial effort, provides a scalable and efficient approach to gathering job listings from a wide array of sources.

---


For more detailed implementation guides, refer to the [project documentation](./ce_llmpr.pdf).

<img width="1000" alt="image" src="https://github.com/AccuPlatform/CrawlingAndScraping/assets/23615297/f048610b-2938-478a-b221-a004e68dffea">
