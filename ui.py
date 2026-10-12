import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_css():
    """Injects a cohesive dark-slate modern theme removing all stark white backgrounds."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Global Typography & Deep Dark Background */
    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
    }

    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 15% 15%, #131b2e 0%, #0b0f19 100%) !important;
        background-attachment: fixed;
    }

    /* Seamless Dark Sidebar (Removes white box/strip) */
    [data-testid="stSidebar"], [data-testid="stSidebarUserContent"], [data-testid="stSidebarHeader"] {
        background-color: #0d1322 !important;
        border-right: 1px solid #1e293b !important;
        color: #e2e8f0 !important;
    }

    /* Modern Styled Metric Cards */
    .metric-card {
        background: rgba(19, 27, 46, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        margin-bottom: 12px;
    }
    .metric-label { 
        font-size: 0.8rem; 
        color: #94a3b8; 
        font-weight: 600; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
    }
    .metric-value { 
        font-size: 1.7rem; 
        font-weight: 700; 
        color: #38bdf8; 
        margin-top: 4px; 
    }

    /* Modern Tabs (No white background or white borders) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #131b2e !important;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #1e293b;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        color: #94a3b8 !important;
        border: none !important;
        background-color: transparent !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }

    /* Subheaders */
    h1, h2, h3, .stSubheader {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    /* Custom File Uploader styling (Removes white drop box) */
    [data-testid="stFileUploader"] {
        background-color: #131b2e;
        border: 1px dashed #334155;
        border-radius: 10px;
        padding: 8px;
    }

    /* Primary Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        padding: 0.55rem 1.25rem !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }

    /* Plotly Card Wrappers */
    [data-testid="stPlotlyChart"] {
        background: rgba(19, 27, 46, 0.6) !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        padding: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_top_kpis(messages: int, users: int, words: int, media: int):
    """Renders 4 top highlight metric cards."""
    c1, c2, c3, c4 = st.columns(4)
    items = [
        ("💬 Total Messages", f"{messages:,}", c1),
        ("👥 Active Users", f"{users:,}", c2),
        ("📝 Total Words", f"{words:,}", c3),
        ("📷 Media Shared", f"{media:,}", c4),
    ]
    for label, val, col in items:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{val}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ----------------- Analytics Tab Visuals -----------------

def render_analytics_tab(user_activity, sentiment_counts, response_by_user, avg_response_time, day_activity, hour_activity, common_words_df, emoji_df):
    """Renders structured tables, progress bars, and emoji sentiment cards in dark theme."""
    
    st.markdown("### ⚡ Activity & Engagement Overview")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">⏱️ Avg Response Time</div>
                <div class="metric-value">{avg_response_time:.2f} <span style="font-size: 1rem; color: #94a3b8;">mins</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with sc2:
        top_user = user_activity.iloc[0]["User"] if not user_activity.empty else "N/A"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">👑 Top Contributor</div>
                <div class="metric-value" style="font-size: 1.3rem;">{top_user}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with sc3:
        dom_sentiment = sentiment_counts.iloc[0]["Sentiment"] if not sentiment_counts.empty else "N/A"
        icon = "😊" if dom_sentiment == "Positive" else ("😡" if dom_sentiment == "Negative" else "😐")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">🎭 Dominant Sentiment</div>
                <div class="metric-value" style="font-size: 1.3rem;">{icon} {dom_sentiment}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👥 User Contribution Share")
        st.dataframe(
            user_activity,
            column_config={
                "User": st.column_config.TextColumn("Member"),
                "Message": st.column_config.NumberColumn("Messages", format="%d 💬"),
                "Percentage": st.column_config.ProgressColumn("Share", format="%.2f%%", min_value=0, max_value=100),
            },
            hide_index=True,
            use_container_width=True
        )

        st.subheader("⏱️ Response Times by User")
        st.dataframe(
            response_by_user,
            column_config={
                "User": st.column_config.TextColumn("Member"),
                "Response_time": st.column_config.NumberColumn("Avg Reply", format="%.2f min ⏳")
            },
            hide_index=True,
            use_container_width=True
        )

    with col2:
        st.subheader("🎭 Sentiment Distribution")
        sentiment_display = sentiment_counts.copy()
        emoji_map = {"Positive": "🟢 Positive 😊", "Neutral": "🟡 Neutral 😐", "Negative": "🔴 Negative 😡"}
        sentiment_display["Sentiment"] = sentiment_display["Sentiment"].map(lambda x: emoji_map.get(x, x))
        
        st.dataframe(
            sentiment_display,
            column_config={
                "Sentiment": st.column_config.TextColumn("Tone"),
                "Count": st.column_config.NumberColumn("Messages"),
                "Percentage": st.column_config.ProgressColumn("Proportion", format="%.2f%%", min_value=0, max_value=100)
            },
            hide_index=True,
            use_container_width=True
        )

        st.subheader("✨ Words & Emojis")
        tab_w, tab_e = st.tabs(["🔤 Top Words", "😀 Top Emojis"])
        with tab_w:
            st.dataframe(common_words_df, hide_index=True, use_container_width=True)
        with tab_e:
            st.dataframe(emoji_df, hide_index=True, use_container_width=True)


# ----------------- Dark Mode Visualizations (Plotly) -----------------

def render_visualizations_tab(daily_timeline, monthly_timeline, day_activity, hour_activity, heatmap_data, common_words_df, emoji_df, response_by_user):
    """Renders interactive Plotly visual charts in dark-slate mode."""
    
    dark_template = "plotly_dark"
    plot_bg = "rgba(0,0,0,0)"

    c1, c2 = st.columns(2)

    with c1:
        # Daily Line Chart
        fig_daily = px.line(
            daily_timeline, x="Date", y="Message", 
            title="📈 Daily Message Volume", template=dark_template
        )
        fig_daily.update_traces(line=dict(color="#38bdf8", width=2.5))
        fig_daily.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg)
        st.plotly_chart(fig_daily, use_container_width=True)

        # Day of Week Horizontal Bar
        fig_day = px.bar(
            day_activity, x="Message", y="Day_name", orientation="h",
            title="📅 Activity by Day of the Week", template=dark_template,
            color_discrete_sequence=["#0284c7"]
        )
        fig_day.update_layout(yaxis=dict(autorange="reversed"), paper_bgcolor=plot_bg, plot_bgcolor=plot_bg)
        st.plotly_chart(fig_day, use_container_width=True)

        # Top Words Bar Chart
        fig_words = px.bar(
            common_words_df.head(15), x="Count", y="Word", orientation="h",
            title="🔤 Top 15 Common Words", template=dark_template,
            color_discrete_sequence=["#a855f7"]
        )
        fig_words.update_layout(yaxis=dict(autorange="reversed"), paper_bgcolor=plot_bg, plot_bgcolor=plot_bg)
        st.plotly_chart(fig_words, use_container_width=True)

        # Response Time Bar Chart
        fig_resp = px.bar(
            response_by_user, x="User", y="Response_time",
            title="⏳ Average Response Time by User (Minutes)", template=dark_template,
            color_discrete_sequence=["#f43f5e"]
        )
        fig_resp.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg)
        st.plotly_chart(fig_resp, use_container_width=True)

    with c2:
        # Monthly Line Chart
        fig_monthly = px.line(
            monthly_timeline, x="Month_Year", y="Message", markers=True,
            title="🗓️ Monthly Timeline Trend", template=dark_template
        )
        fig_monthly.update_traces(line=dict(color="#2dd4bf", width=2.5), marker=dict(size=7))
        fig_monthly.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg)
        st.plotly_chart(fig_monthly, use_container_width=True)

        # Hourly Activity Bar Chart
        fig_hour = px.bar(
            hour_activity, x="Hour", y="Message",
            title="⏰ Activity by Hour of the Day", template=dark_template,
            color_discrete_sequence=["#6366f1"]
        )
        fig_hour.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg)
        st.plotly_chart(fig_hour, use_container_width=True)

        # Day x Hour Heatmap
        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day", y="Day of Week", color="Messages"),
            x=heatmap_data.columns, y=heatmap_data.index,
            color_continuous_scale="Viridis",
            title="🔥 Day × Hour Activity Heatmap", aspect="auto",
            template=dark_template
        )
        fig_heat.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg)
        st.plotly_chart(fig_heat, use_container_width=True)

        # Emoji Bar Chart
        fig_emoji = px.bar(
            emoji_df.head(10), x="Emoji", y="Count",
            title="😀 Top 10 Most Used Emojis", template=dark_template,
            color_discrete_sequence=["#f59e0b"]
        )
        fig_emoji.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg)
        st.plotly_chart(fig_emoji, use_container_width=True)