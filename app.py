import streamlit as st
import pandas as pd
from parser import parse_chat
from collections import Counter
import nltk
from nltk.corpus import stopwords
import re
import emoji
from textblob import TextBlob
import ui



st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# Apply UI CSS & theme
ui.load_css()

if "analyzed" not in st.session_state:
    st.session_state["analyzed"] = False

if "chat_data" not in st.session_state:
    st.session_state["chat_data"] = None

st.title("💬 WhatsApp Chat Analyzer")
st.caption("Upload your exported WhatsApp chat (.txt) to explore interactive insights and AI summaries.")
st.divider()

# Sidebar
st.sidebar.title("📁 Menu")
st.sidebar.write("Upload your chat to begin analysis")

uploaded_file = st.sidebar.file_uploader(
    "Choose your WhatsApp Chat",
    type=["txt"]
)

if st.sidebar.button("🚀 Analyze", use_container_width=True):
    if uploaded_file is not None:
        data = uploaded_file.getvalue().decode("utf-8")
        st.session_state["chat_data"] = data
        st.session_state["analyzed"] = True
    else:
        st.sidebar.warning("Please upload a chat first")

try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

if not st.session_state["analyzed"] or st.session_state["chat_data"] is None:
    st.info("👈 Upload a WhatsApp chat from the sidebar and click **Analyze**")
else:
    data = st.session_state["chat_data"]
    df = parse_chat(data)

    # Global KPI Calculations
    users = sorted(df['User'].unique().tolist())
    total_messages = df.shape[0]
    total_users = df['User'].nunique()
    total_words = df['Message'].str.split().str.len().sum()
    media_shared = df[df["Message"] == '<Media omitted>'].shape[0]

    # Render Top Metric Banner
    ui.render_top_kpis(total_messages, total_users, total_words, media_shared)

    # Data Processing for Tabs
    daily_timeline = df.groupby('Date')['Message'].count().reset_index()
    monthly_timeline = df.groupby("Month_Year")["Message"].count().reset_index()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_activity = df.groupby("Day_name")["Message"].count().reset_index()
    day_activity['Day_name'] = pd.Categorical(day_activity['Day_name'], categories=days, ordered=True)
    day_activity = day_activity.sort_values("Day_name")

    hours = pd.DataFrame({"Hour": range(24)})
    hour_grouped = df.groupby("Hour")["Message"].count().reset_index()
    hour_activity = hours.merge(hour_grouped, on="Hour", how="left").fillna(0)

    heatmap_data = df.groupby(['Day_name', 'Hour'])["Message"].count().reset_index()
    heatmap_data = heatmap_data.pivot(index="Day_name", columns="Hour", values="Message").reindex(days).fillna(0)

    user_activity = df.groupby("User")["Message"].count().reset_index().sort_values("Message", ascending=False)
    user_activity["Percentage"] = (user_activity["Message"] / total_messages * 100).round(2)

    df_text = df[df["Message"] != "<Media omitted>"]
    words = [re.sub(r"[^a-zA-Z]", "", w.lower()) for w in " ".join(df_text["Message"]).split()]
    filtered_words = [w for w in words if w and w not in stop_words]
    common_words_df = pd.DataFrame(Counter(filtered_words).most_common(20), columns=["Word", "Count"])

    emoji_counts = Counter()
    for message in df["Message"]:
        for character in message:
            if character in emoji.EMOJI_DATA:
                emoji_counts[character] += 1
    emoji_df = pd.DataFrame(emoji_counts.most_common(20), columns=["Emoji", "Count"])

    # Response Time Calculation
    df['previous_user'] = df["User"].shift(1)
    df["Response_time"] = (df["DateTime"] - df["DateTime"].shift(1)).dt.total_seconds() / 60
    response_df = df[(df["User"] != df["previous_user"]) & (df["Response_time"] <= 120)].copy()
    avg_response_time = response_df["Response_time"].mean() if not response_df.empty else 0.0
    response_by_user = response_df.groupby("User")["Response_time"].mean().reset_index().sort_values("Response_time")

    # Sentiment Analysis
    df['Sentiment_score'] = df["Message"].apply(lambda msg: TextBlob(msg).sentiment.polarity)
    def get_sentiment(score):
        return "Positive" if score > 0 else ("Negative" if score < 0 else "Neutral")
    df['Sentiment'] = df["Sentiment_score"].apply(get_sentiment)
    sentiment_counts = df["Sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["Sentiment", "Count"]
    sentiment_counts["Percentage"] = (sentiment_counts["Count"] / sentiment_counts["Count"].sum() * 100).round(2)

    # Prepare summary data for Gemini
    summary_data = {
        "total_messages": total_messages,
        "total_users": total_users,
        "total_words": total_words,
        "media_shared": media_shared,
        "average_response_time": round(avg_response_time, 2),
        "sentiment": sentiment_counts.to_dict(orient="records"),
        "most_active_users": user_activity.head(5).to_dict(orient="records")
    }

    # Tabs Layout
    tab1, tab2, tab3 = st.tabs(["💬 Chat & AI Summary", "📊 Analytics", "📈 Visualizations"])

    with tab1:
        st.subheader("Chat Preview")
        st.dataframe(df, use_container_width=True)


    with tab2:
        ui.render_analytics_tab(
            user_activity, sentiment_counts, response_by_user,
            avg_response_time, day_activity, hour_activity,
            common_words_df, emoji_df
        )

    with tab3:
        ui.render_visualizations_tab(
            daily_timeline, monthly_timeline, day_activity,
            hour_activity, heatmap_data, common_words_df,
            emoji_df, response_by_user
        )