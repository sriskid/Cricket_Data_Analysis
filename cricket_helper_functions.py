import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

def create_csv():
    df = pd.DataFrame(columns=["Name", "URL"])
    df.to_csv("player_links.csv", index=False)

def insert_player_link(name, url):
    data = pd.read_csv("player_links.csv")
    if name in data["Name"].tolist():
        print("Name is already in the data")
        return
    new_row = {"Name": name, "URL": url}
    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

    data.to_csv("player_links.csv", index=False)

def parse_hrefs(match_hrefs):
    match_urls = []
    for href in match_hrefs:
        if "/ci/engine/match" in href:
            match_urls.append("https://stats.espncricinfo.com"+href)
    
    return match_urls[2:]

def get_match_url(url):
    page_to_scrape = requests.get(url)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    match_urls = soup.find_all("a")
    urls = [url["href"] for url in match_urls]
    match_urls = parse_hrefs(urls)
    return match_urls

def parse_not_out(data):
    data = data.copy()
    data["Runs"] = [re.sub(r"\*", "",str(run)) for run in data["Runs"]]
    data["Runs"] = data["Runs"].astype("int")
    return data

def get_innings_dataframe(url):
    df = pd.read_html(url)[3]
    match_urls = get_match_url(url)[:len(df.index)]
    df["Match URL"] = match_urls
    df = df.loc[(df["Runs"] != "DNB") & (df["Runs"] != "TDNB")].reset_index(drop=True)
    df.drop(df.columns[[9,13]], axis = 1, inplace=True)
    df["Start Date"] = pd.to_datetime(df["Start Date"], format="%d %b %Y")
    df = parse_not_out(df)
    
    return df

def get_career_average_list(data):
    averages = []
    runs = 0
    num_innings = 0
    dismissals = data["Dismissal"].tolist()
    for run, dismissal in zip(data["Runs"].tolist(), dismissals):
        if re.search(r"not\s*out", dismissal):
            runs += run
            if num_innings == 0:
                continue
            average = runs/num_innings
        else:
            runs += run
            num_innings +=1 
            average = runs/num_innings
        averages.append(average)

    return averages
    