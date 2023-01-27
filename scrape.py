import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://au.linkedin.com/jobs/search?keywords=Pharmacist&location=Sydney%2C%20New%20South%20Wales%2C%20Australia&geoId=104769905&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0")
driver.maximize_window()

# Find number of results
num_jobs = str(driver.find_element(By.CLASS_NAME, "results-context-header__job-count").text)

# Scroll and try to click show more button, if not keep scrolling

# Find element containing job listings 
jobs_list = driver.find_element(By.CLASS_NAME, "jobs-search__results-list")
jobs = jobs_list.find_elements(By.TAG_NAME, "li")

records = []
field_names = ["job_id",
                   "job_title",
                   "compnay" ,
                   "location" ,
                   "link" ,
                   "date",
                   "seniority",
                   "employment_type",
                   "job_function",
                   "industries"]

for job in jobs:
    job_id = (str(job.find_element(By.CSS_SELECTOR, "div").get_attribute('data-entity-urn'))[-10:])
    job_title = (job.find_element(By.CSS_SELECTOR, "h3").text)
    company = (job.find_element(By.CSS_SELECTOR, "h4").get_attribute("innerText"))
    location = (job.find_element(By.CLASS_NAME, "job-search-card__location").text)
    link = (job.find_element(By.CSS_SELECTOR, "a").get_attribute("href"))
    job_dict = {"job_id": job_id, 
                   "job_title": job_title, 
                   "compnay": company, 
                   "location": location, 
                   "link": link,
    }
    try:
        date = (job.find_element(By.CLASS_NAME, "job-search-card__listdate").get_attribute("datetime"))
    except:
        date = (job.find_element(By.CLASS_NAME, "job-search-card__listdate--new").get_attribute("datetime"))
    # For each job listing click onto it and extract information
    job.click()
    # sleep to allow page to load
    time.sleep(3)
    # however sometimes information page won't load even after a large delay, if so continue onto next listing 
    try:
        criteria = driver.find_element(By.CLASS_NAME, "description__job-criteria-list")
        catergorys = criteria.find_elements(By.CSS_SELECTOR, "h3")
        details = criteria.find_elements(By.CSS_SELECTOR, "span")
        seniority = 'N/A'
        for i in range(len(details)):
            if catergorys[i].get_attribute("innerText") == "Seniority level":
                seniority = (details[i].get_attribute("innerText"))
            
            elif catergorys[i].get_attribute("innerText") == "Employment type":
                employment_type = (details[i].get_attribute("innerText"))
                
            elif catergorys[i].get_attribute("innerText") == "Job function":
                job_function = (details[i].get_attribute("innerText"))
                
            elif catergorys[i].get_attribute("innerText") == "Industries":
                industries = (details[i].get_attribute("innerText"))
        # some postings will only include employment type, if so add N/A to the rest 
        if seniority == "N/A":
            job_function = ("N/A")
            industries = ("N/A")
    except:
        records.append(job_dict)
        continue
    job_dict["date"] = date
    job_dict["seniority"] = seniority
    job_dict["employment_type"] = employment_type
    job_dict["job_function"] = job_function
    job_dict["industries"] = industries
    records.append(job_dict)

with open("jobs.csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(records)