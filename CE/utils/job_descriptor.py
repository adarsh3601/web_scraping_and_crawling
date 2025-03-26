from CE.logger_config import logger

def is_job_description_page(html_content):
    # Common keywords found in job description pages
    job_keywords = [
        "responsibilities", "qualification", "skills", "requirements",
        "duties", "role summary", "position overview", "employment type",
        "full time", "part time", "contract", "temporary", "internship", "remote",
        "apply", "application", "cover letter", "resume", "benefits", "compensation",
        "salary", "experience", "education", "certified", "licensed", "mission",
        "values", "culture", "diversity", "inclusion", "opportunities", "travel required",
        "equal opportunity employer", "description", "posted", "what you'll do",
        "what you need", "salary information", "applying for this role", "summary of the role",

    ]
    req_words = ["what you'll do", 'equal opportunity', 'equal opportunity employer']

    # Prepare the soup
    # soup = BeautifulSoup(html_content, 'html.parser')

    # Extract text from the HTML content
    text = html_content.get_text().lower()
    
    # Check for the presence of job-related structured data (schema.org JobPosting)
    if 'application/ld+json' in html_content:
        if '"@type": "jobposting"' in html_content.lower():
            print("application json")
            return True
    
    # Count the occurrences of job-related keywords
    unique_keywords_present = {word for word in job_keywords if word in text}
    
    # Determine if the content is likely a job description
    # This threshold can be adjusted based on the desired sensitivity
    # if len(unique_keywords_present) > 9:
    # logger.info(f"keyword count {len(unique_keywords_present)}, {unique_keywords_present}")
    # return len(unique_keywords_present) > 9 or \
    # ('equal opportunity employer' in unique_keywords_present and len(unique_keywords_present)>7)
    for word in req_words:
        if word in text:
            # print(f"word in text {word}")
            return 1
    return 0

def check_job_descriptors(url1,url2):
    # print("desc123")
    # print(url1)
    # print(url2)
    segments1 = url1.split('/')
    segments2 = url2.split('/')
    segments1 = [x for x in segments1 if x!='']
    segments2 = [x for x in segments2 if x!='']
    # Ensure both URLs have the same number of segments
    if len(segments1) != len(segments2):
        return False
    
    # Count the number of segments that are different
    differences = 0
    for seg1, seg2 in zip(segments1, segments2):
        if seg1 != seg2:
            differences += 1
            
            # If there is more than one difference, return False immediately
            if differences > 1:
                return False
    
    # Return True if there is exactly one difference, otherwise False
    return differences == 1