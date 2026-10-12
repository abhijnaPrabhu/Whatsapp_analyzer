import re
import pandas as pd


def parse_chat(data):

    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s([^:]+):\s(.*)"

    dates = []
    times = []
    users = []
    messages = []

    for line in data.splitlines():

        match = re.match(pattern, line)

        if match:

            dates.append(match.group(1))
            times.append(match.group(2))
            users.append(match.group(3))
            messages.append(match.group(4))

    df = pd.DataFrame({
        "Date": dates,
        "Time": times,
        "User": users,
        "Message": messages
    })


    #feature engineering
    df["DateTime"]=pd.to_datetime(
        df["Date"]+" "+df["Time"],
        dayfirst=True
    )

    df["Year"]=df["DateTime"].dt.year
    df["Month_num"]=df["DateTime"].dt.month
    df["Month"]=df["DateTime"].dt.month_name()
    df["Day"]=df["DateTime"].dt.day
    df["Day_name"]=df["DateTime"].dt.day_name()
    df["Hour"]=df["DateTime"].dt.hour
    df['Month_Year']=(
        df["Month"] +" "+ df["Year"].astype(str)
    )

    return df