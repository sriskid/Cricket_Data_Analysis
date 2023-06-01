import pandas as pd
import re

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

def get_innings_dataframe(url):
    df = pd.read_html(url)[3]
    df = df.loc[(df["Runs"] != "DNB") & (df["Runs"] != "TDNB")].reset_index(drop=True)
    df.drop(df.columns[[9,13]], axis = 1, inplace=True)
    df["Start Date"] = pd.to_datetime(df["Start Date"], format="%d %b %Y")

    return df

def parse_not_out(data):
    data = data.copy()
    data["Runs"] = [re.sub(r"\*", "",str(run)) for run in data["Runs"]]
    data["Runs"] = data["Runs"].astype("int")
    return data

def get_career_average_list(data):
    averages = []
    runs = 0
    num_innings = 0
    for run in data["Runs"].tolist():
        if "*" in [*run]:
            run = int(run[:-1])
            runs += run
            if num_innings == 0:
                continue
            average = runs/num_innings
        else:
            runs += int(run)
            num_innings +=1 
            average = runs/num_innings
        averages.append(average)

    return averages
    