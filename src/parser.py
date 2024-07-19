import requests
from bs4 import BeautifulSoup

url = "https://djinni.co/jobs/?primary_keyword=Python&exp_level=no_exp&exp_level=1y&exp_level=2y"


def fetch_jobs_from_djinni():
    global url

    request = requests.get(url)
    src = request.text
    soup = BeautifulSoup(src, "html.parser")
    job_listings = soup.find_all("div", class_="job-list-item position-relative")

    results = []

    for job_listing in job_listings:
        job_title_element = job_listing.find("a", class_="h3 job-list-item__link")

        job_title = job_listing.find("a", class_="h3 job-list-item__link").get_text(
            strip=True
        )
        vacancy_link = job_title_element["href"]
        company_name = job_listing.find("a", class_="mr-2").get_text(strip=True)
        publication_date = job_listing.find("span", class_="mr-2 nobr").get("title")

        results.append(
            {
                "job_title": job_title,
                "vacancy_link": vacancy_link,
                "company_name": company_name,
                "publication_date": publication_date,
            }
        )

    return results
