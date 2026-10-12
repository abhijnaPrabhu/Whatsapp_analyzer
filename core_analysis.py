import streamlit as st
import pandas as pd
import seaborn as sns
from parser import parse_chat
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.corpus import stopwords
import re
import emoji
from textblob import TextBlob


st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

if "analyzed" not in st.session_state:
    st.session_state["analyzed"]=False

if "chat_data" not in st.session_state:
    st.session_state["chat_data"]=None

st.write(
    """
    # Upload your exported Whatsapp Chat and explore detailed insights
    """
)

#SIDE BAR FUNCTIONS
st.sidebar.title("Menu")
st.sidebar.write("Upload your chat to begin analysis")

uploaded_file=st.sidebar.file_uploader(
    "Choose your Whatsapp Chat",
    type=["txt"]
)

if st.sidebar.button("Analyze"):

    if uploaded_file is not None:

        data=uploaded_file.getvalue().decode("utf-8")
        st.session_state["chat_data"]=data
        st.session_state["analyzed"]=True

    else:
        st.sidebar.warning("Please upload a chat first")

stop_words=set(stopwords.words("english"))

if (
    not st.session_state["analyzed"]
    or st.session_state["chat_data"] is None
):

    st.info(
        "Upload a WhatsApp chat from the sidebar and click Analyze"
    )

else:

    data=st.session_state["chat_data"]

    df=parse_chat(data)

    tab1,tab2,tab3=st.tabs([
        "Chat",
        "Analytics",
        "Visualization"
    ])


        

    users=sorted(df['User'].unique().tolist())

    total_messages=df.shape[0]
    total_users=df['User'].nunique()
    total_words=df['Message'].str.split().str.len().sum()
    media_shared=df[df["Message"]=='<Media omitted>'].shape[0]



    with tab2:
        st.subheader('Quick Statistics')
        col1,col2,col3,col4=st.columns(4)

        #daily_timeline
        #------------------------------
        st.subheader("Daily_timeline")

        daily_timeline=(
            df.groupby('Date')['Message']
            .count()
            .reset_index()
        )

        st.dataframe(daily_timeline)

        #monthly_timeline
        #---------------------------------
        st.subheader("Monthly Timeline data")

        monthly_timeline=(
            df.groupby("Month_Year")["Message"]
            .count()
            .reset_index()
        )

        st.dataframe(monthly_timeline)

        #Activity by day
        #-----------------------------------------
        st.subheader("Activity by day of the week")

        day_activity=(
            df.groupby("Day_name")["Message"]
            .count()
            .reset_index()
        )

        days=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        day_activity['Day_name']=pd.Categorical(
            day_activity['Day_name'],
            categories=days,
            ordered=True
        )

        day_activity=day_activity.sort_values("Day_name")

        st.dataframe(day_activity)

        #Activity by hour
        #-------------------------------
        hour_activity=(
            df.groupby("Hour")["Message"]
            .count()
            .reset_index()
        )

        hours=pd.DataFrame({
            "Hour":range(24)
        })

        hour_activity=hours.merge(
            hour_activity,
            on="Hour",
            how="left"
        )

        hour_activity["Message"]=(
            hour_activity["Message"].fillna(0)
        )

        st.subheader("Activity by Hour")
        st.dataframe(hour_activity)

        #Day x Hour heatmap
        #--------------------
        heatmap_data=(
            df.groupby(
                ['Day_name','Hour']
            )["Message"]
            .count()
            .reset_index()
        )

        heatmap_data=heatmap_data.pivot(
            index="Day_name",
            columns="Hour",
            values="Message"
        )

        heatmap_data=heatmap_data.reindex(days)
        heatmap_data=heatmap_data.fillna(0)

        st.subheader("Activity Heatmap Data")
        st.dataframe(heatmap_data)

        #user activity
        #-------------------
        user_activity=(
            df.groupby("User")["Message"]
            .count()
            .reset_index()
        )

        user_activity=user_activity.sort_values(
            "Message",
            ascending=False
        )

        st.subheader('Most active users')

        total_chat_messages=user_activity["Message"].sum()

        user_activity["Percentage"]=(
            user_activity["Message"]
            /total_chat_messages
            *100
        )

        user_activity['Percentage']=(
            user_activity["Percentage"].round(2)
        )

        st.dataframe(
            user_activity,
            column_config={
                "Message":"Messages",
                "Percentage":st.column_config.NumberColumn(
                    "Contribution %",
                    format="%.2f%%"
                )
            }
        )

        #most common words
        #------------------------
        df_text=df[
            df["Message"]!="<Media omitted>"
        ]

        all_messages=" ".join(
            df_text["Message"]
        )

        all_messages=all_messages.lower()

        words=all_messages.split()

        filtered_words=[]

        for word in words:

            word=re.sub(
                r"[^a-zA-Z]",
                "",
                word
            )

            if word and word not in stop_words:
                filtered_words.append(word)

        word_counts=Counter(filtered_words)

        common_words=word_counts.most_common(20)

        common_words_df=pd.DataFrame(
            common_words,
            columns=["Word","Count"]
        )

        st.subheader("Most Common Words")
        st.dataframe(common_words_df)

        #Emoji analysis
        #--------------------
        emoji_counts=Counter()

        for message in df["Message"]:

            for character in message:

                if character in emoji.EMOJI_DATA:
                    emoji_counts[character]+=1

        emoji_df=pd.DataFrame(
            emoji_counts.most_common(20),
            columns=["Emoji","Count"]
        )

        st.subheader("Most Used Emojis")
        st.dataframe(emoji_df)

        #Response-time analysis
        #-------------------------------
        df['previous_user']=df["User"].shift(1)

        df["Response_time"]=(
            df["DateTime"]-df["DateTime"].shift(1)
        ).dt.total_seconds()/60

        response_df=df[
            df["User"]!=df["previous_user"]
        ].copy()

        response_df=response_df[
            response_df["Response_time"]<=120
        ]

        avg_response_time=response_df["Response_time"].mean()

        st.subheader("Avg Response Time")

        st.metric(
            "Average Response Time",
            f"{avg_response_time:.2f} minutes"
        )

        st.subheader('Response Time data')

        st.dataframe(
            response_df[
                [
                    "User",
                    "previous_user",
                    "Response_time"
                ]
            ]
        )

        #response time by user
        #-------------------------
        response_by_user=(
            response_df
            .groupby("User")["Response_time"]
            .mean()
            .reset_index()
        )

        response_by_user=response_by_user.sort_values(
            "Response_time"
        )

        st.subheader("Average response time by user")
        st.dataframe(response_by_user)

        #sentiment analysis
        #--------------------------
        st.subheader("Sentiment Analysis")

        df['Sentiment_score']=df["Message"].apply(
            lambda message:
            TextBlob(message).sentiment.polarity
        )

        def get_sentiment(score):

            if score>0:
                return "Positive"

            elif score<0:
                return "Negative"

            else:
                return "Neutral"

        df['Sentiment']=df["Sentiment_score"].apply(
            get_sentiment
        )

        st.dataframe(
            df[
                [
                    "User",
                    "Message",
                    "Sentiment_score",
                    "Sentiment"
                ]
            ]
        )

        #sentiment distribution
        #---------------------------

        sentiment_counts=(
            df["Sentiment"]
            .value_counts()
            .reset_index()
        )

        sentiment_counts.columns=[
            "Sentiment",
            "Count"
        ]

        st.subheader("Sentiment Distribution")

        sentiment_counts["Percentage"]=(
            sentiment_counts["Count"]
            /sentiment_counts["Count"].sum()
            *100
        ).round(2)

        st.dataframe(sentiment_counts)

        #Chat summary statistics
        #---------------------------
        summary_data={
            "total_messages":total_messages,
            "total_users":total_users,
            "total_words":total_words,
            "media_shared":media_shared,
            "average_response_time":round(
                avg_response_time,
                2
            )
        }

        summary_data["sentiment"]=(
            sentiment_counts.to_dict(
                orient="records"
            )
        )

        summary_data["most_active_users"]=(
            user_activity
            .head(5)
            .to_dict(
                orient="records"
            )
        )



        with col1:
            st.metric(
                'Message',
                total_messages
            )

        with col2:
            st.metric(
                'User',
                total_users
            )

        with col3:
            st.metric(
                'Words',
                total_words
            )

        with col4:
            st.metric(
                'Media',
                media_shared
            )

    with tab3:

        st.info(
            "Charts will be displayed here after analysis"
        )

        #Daily timeline analysis
        #-----------------------

        fig,ax=plt.subplots(
            figsize=(10,5)
        )

        ax.plot(
            daily_timeline["Date"],
            daily_timeline["Message"],
            marker="o"
        )

        ax.set_title("Daily timeline")
        ax.set_xlabel("Date")
        ax.set_ylabel("Message")

        fig.autofmt_xdate()

        st.pyplot(fig)

        #Monthly timeline Analysis
        #-------------------------

        fig,ax=plt.subplots(
            figsize=(10,5)
        )

        ax.plot(
            monthly_timeline['Month_Year'],
            monthly_timeline['Message'],
            marker='o'
        )

        ax.set_title("Monthly Timeline")
        ax.set_xlabel("Month")
        ax.set_ylabel("Messages")

        plt.xticks(
            rotation=45
        )

        st.pyplot(fig)

        #Day of Week
        #-------------------------

        fig,ax=plt.subplots(
            figsize=(10,5)
        )

        ax.barh(
            day_activity['Day_name'],
            day_activity['Message']
        )

        ax.set_xlabel('Day')
        ax.set_ylabel('Message')
        ax.set_title(
            "Messages by day of the week"
        )

        st.pyplot(fig)

        #hour of the day
        #-------------------------

        fig,ax=plt.subplots(
            figsize=(10,5)
        )

        ax.bar(
            hour_activity["Hour"],
            hour_activity["Message"]
        )

        ax.set_xlabel("Hour")
        ax.set_ylabel("Messages")
        ax.set_title(
            "Messages by hour of the day"
        )

        st.pyplot(fig)

        #heat-map
        #-------------------------

        fig,ax=plt.subplots(
            figsize=(12,5)
        )

        sns.heatmap(
            heatmap_data,
            ax=ax,
            annot=True,
            fmt=".0f"
        )

        ax.set_xlabel(
            "Hour of the Day"
        )

        ax.set_ylabel(
            "Day of the Week"
        )

        st.pyplot(fig)

        #common words chart
        #-------------------------

        st.subheader("Most Common Words")

        fig,ax=plt.subplots(
            figsize=(10,6)
        )

        ax.barh(
            common_words_df["Word"],
            common_words_df["Count"]
        )

        ax.set_xlabel("Count")
        ax.set_ylabel("Word")
        ax.set_title(
            "Most Common Words"
        )

        ax.invert_yaxis()

        st.pyplot(fig)

        #emoji analysis
        #-------------------------

        st.subheader(
            'Most used Emojis'
        )

        fig,ax=plt.subplots(
            figsize=(10,6)
        )

        ax.bar(
            emoji_df["Emoji"],
            emoji_df["Count"]
        )

        ax.set_xlabel("Emoji")
        ax.set_ylabel("Count")
        ax.set_title(
            "Most used Emojis"
        )

        st.pyplot(fig)

        #Response time by user
        #-------------------------

        st.subheader(
            "Average response time by user"
        )

        fig,ax=plt.subplots(
            figsize=(10,5)
        )

        ax.bar(
            response_by_user["User"],
            response_by_user["Response_time"]
        )

        ax.set_xlabel("User")

        ax.set_ylabel(
            "Average response time (minutes)"
        )

        ax.set_title(
            "Average Response time by user"
        )

        plt.xticks(
            rotation=45
        )

        st.pyplot(fig)

    with tab1:
        st.subheader('Chat preview')
        st.dataframe(df)


            