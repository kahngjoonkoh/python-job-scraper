from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
import requests
import csv

def get_so_jobs(term):
  job_list = []
  url = f"https://stackoverflow.com/jobs?r=true&q={term}"
  html_doc = requests.get(url).text
  soup = BeautifulSoup(html_doc, "html.parser")
  list_results = soup.find("div", {"class":"listResults"})
  head_soup = list_results.find_all("h2", {"class":"mb4 fc-black-800 fs-body3"})
  for head in head_soup:
    header = head.find("a")
    link = "https://stackoverflow.com" + header.get("href")
    title = header.get_text()
    job_list.append([title, "company_name", link])
  comp_soup = list_results.find_all("h3", {"class":"fc-black-700 fs-body1 mb4"})
  for i, company in enumerate(comp_soup):
    comp_name = company.find("span").text.strip()
    job_list[i][1] = comp_name

  return job_list


def get_wwr_jobs(term):
  job_list = []
  url = f"https://weworkremotely.com/remote-jobs/search?term={term}"
  html_doc = requests.get(url).text
  soup = BeautifulSoup(html_doc, "html.parser")
  list_soup = soup.find("ul")
  list_item = list_soup.find_all("li", {"class":"feature"})
  for info in list_item:
    title = info.find("span", {"class":"title"}).text
    company = info.find("span", {"class":"company"}).text
    link = "https://weworkremotely.com" + info.find("a").get("href")
    job_list.append([title, company, link])
  
  return job_list


def get_remo_jobs(term):
  job_list = []
  url = f"https://remoteok.io/remote-dev+{term}-jobs"
  html_doc = requests.get(url).text
  soup = BeautifulSoup(html_doc, "html.parser")
  tr_soup = soup.find_all("tr", {"class":"job"})
  for tr in tr_soup:
    title = tr.find("h2", {"itemprop":"title"}).text
    company = tr.get("data-company")
    link = "https://remoteok.io" + tr.get("data-href")
    job_list.append([title, company, link])

  return job_list


def write_csv(job_list):
  with open("jobs.csv", "w") as file:
    writer = csv.writer(file)
    for job_info in job_list:
      writer.writerow(job_info)
    file.close()

db= {}
app = Flask("RemoteJobs")

@app.route("/")
def home():
  return render_template("home.html")

@app.route("/search")
def search():
  global job_list
  search_key = request.args.get("term").lower()
  if search_key in db.keys():
    job_list = db[search_key]
  else:
    job_list = get_so_jobs(search_key) + get_wwr_jobs(search_key) + get_remo_jobs(search_key)
    db[search_key] = job_list

  return render_template("search.html", term=search_key, job_list=job_list, length=len(job_list))

@app.route("/jobs.csv")
def export_file():
  write_csv(job_list)
  return send_file("jobs.csv")



app.run(host="0.0.0.0")