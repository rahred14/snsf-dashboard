import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud

# Set page configuration
st.set_page_config(page_title="SNSF Explorer", layout="wide", page_icon="📚")

# Load CSV files from the data folder
grant_df = pd.read_csv("data/Grant.csv")
person_df = pd.read_csv("data/Person.csv")
institute_df = pd.read_csv("data/Institute.csv")
grant_to_person_df = pd.read_csv("data/GrantToPerson.csv")
grant_to_discipline_df = pd.read_csv("data/GrantToDiscipline.csv")
discipline_df = pd.read_csv("data/Discipline.csv")
grant_keyword_df = pd.read_csv("data/GrantToKeyword.csv")
keyword_df = pd.read_csv("data/Keyword.csv")


st.markdown("""
    <style>
    .main-title {
        font-size: 2.4rem;
        font-weight: bold;
        color: #1a1a1a;
        background: linear-gradient(to right, #C9D6FF, #E2E2E2);
        padding: 1.2rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-title {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: bold;
        color: #111;
    }
    .about-box {
        background-color: #f0f4f8;
        padding: 1.2rem;
        border-left: 6px solid #0e76a8;
        border-radius: 8px;
        margin-top: 2rem;
    }
    .custom-nav button {
        width: 200px !important;
        margin-bottom: 10px;
        font-size: 16px;
        padding: 10px 0;
        background: none;
        border: 2px solid #002B36;
        border-radius: 6px;
        font-weight: bold;
        color: #000;
    }
    .custom-nav button:hover {
        background-color: #002B36;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------- Sidebar Navigation ---------------------------
with st.sidebar:
    st.markdown("<div class='custom-nav'>", unsafe_allow_html=True)
    if st.button("Overview"):
        st.session_state.page = "Overview"
    if st.button("Explore Trends"):
        st.session_state.page = "Explore Trends"
    if st.button("Research Topics"):
        st.session_state.page = "Research Topics"
    if st.button("Diversity Insights"):
        st.session_state.page = "Diversity Insights"
    if st.button("Collaboration Network"):
        st.session_state.page = "Collaboration Network"
    if st.button("AI Insights"):
        st.session_state.page = "AI Insights"
    st.markdown("</div>", unsafe_allow_html=True)

# Default page state
if "page" not in st.session_state:
    st.session_state.page = "Overview"

page = st.session_state.page

# --------------------------- Overview ---------------------------
if page == "Overview":
    st.markdown('<div class="main-title">🔍 Welcome to the SNSF Explorer</div>', unsafe_allow_html=True)

    st.markdown("Explore Swiss National Science Foundation (SNSF) research funding data interactively.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title"> Total Grants</div>
                <div class="metric-value">{len(grant_df):,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title"> Total Funding (CHF)</div>
                <div class="metric-value">{grant_df['AmountGrantedAllSets'].sum():,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title"> Total Researchers</div>
                <div class="metric-value">{person_df['PersonNumber'].nunique():,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title"> Total Institutions</div>
                <div class="metric-value">{institute_df['InstituteNumber'].nunique():,}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="about-box">
        <b>This dashboard enables stakeholders, analysts, and policy makers to:</b>
        <ul>
            <li> Explore funding distribution across disciplines, years, and institutions</li>
            <li> Understand AI research trends and diversity metrics</li>
            <li> Visualize researcher collaboration networks</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --------------------------- Explore Trends ---------------------------
elif page == "Explore Trends":
    st.title("📊 Explore Funding Trends")

    with st.sidebar:
        st.markdown("###  Filters")
        year_min, year_max = int(grant_df["CallDecisionYear"].min()), int(grant_df["CallDecisionYear"].max())
        year_range = st.slider("Select Year Range:", min_value=year_min, max_value=year_max, value=(year_min, year_max))

        fund_min = int(grant_df['AmountGrantedAllSets'].min())
        fund_max = int(grant_df['AmountGrantedAllSets'].max())
        fund_range = st.slider("Funding Amount (CHF):", 0, fund_max, (0, fund_max))

        disciplines = ["All"] + sorted(grant_df['MainDiscipline'].dropna().unique())
        selected_discipline = st.selectbox("Select Discipline:", disciplines)

        institutions = ["All"] + sorted(grant_df['Institute'].dropna().unique())
        selected_institution = st.selectbox("Select Institution:", institutions)

    # Apply filters
    filtered_df = grant_df[
        (grant_df['CallDecisionYear'] >= year_range[0]) & (grant_df['CallDecisionYear'] <= year_range[1])]
    filtered_df = filtered_df[
        (filtered_df['AmountGrantedAllSets'] >= fund_range[0]) & (filtered_df['AmountGrantedAllSets'] <= fund_range[1])]
    if selected_discipline != "All":
        filtered_df = filtered_df[filtered_df['MainDiscipline'] == selected_discipline]
    if selected_institution != "All":
        filtered_df = filtered_df[filtered_df['Institute'] == selected_institution]

    # 1. Grants Awarded per Year
    grants_per_year = filtered_df.groupby("CallDecisionYear").size()
    st.subheader("1. Grants Awarded per Year")
    st.bar_chart(grants_per_year)

    # 2. Total Funding per Year
    funding_per_year = filtered_df.groupby("CallDecisionYear")["AmountGrantedAllSets"].sum()
    st.subheader("2. Total Funding per Year")
    st.line_chart(funding_per_year)

    # 3. Top 10 Funded Researchers
    merged_person = pd.merge(grant_to_person_df, grant_df[['GrantNumber', 'AmountGrantedAllSets']], on='GrantNumber')
    merged_person = pd.merge(merged_person, person_df[['PersonNumber', 'FirstName', 'Surname']], on='PersonNumber')
    merged_person['FullName'] = merged_person['FirstName'] + ' ' + merged_person['Surname']
    top_researchers = merged_person.groupby('FullName')['AmountGrantedAllSets'].sum().nlargest(10)
    st.subheader("3. Top 10 Funded Researchers")
    st.bar_chart(top_researchers)

    # 4. Top 10 Funded Institutions
    top_institutes = filtered_df.groupby("Institute")["AmountGrantedAllSets"].sum().nlargest(10)
    st.subheader("4. Top 10 Funded Institutions")
    st.bar_chart(top_institutes)

# --------------------------- Research Topics ---------------------------
elif page == "Research Topics":
    st.title(" Research Topics (NLP Keywords)")

    # Filter UI
    st.sidebar.markdown("### 🔎 Filters")
    keyword_options = sorted(keyword_df['Word'].dropna().astype(str).unique())
    search_term = st.sidebar.text_input("Search Keyword:", "")
    min_freq = st.sidebar.slider("Minimum Keyword Frequency:", 1, 500, 50)
    top_n = st.sidebar.slider("Top N Keywords:", 5, 50, 20)

    # Merge data
    merged_keywords = pd.merge(grant_keyword_df, keyword_df, left_on='KeywordId', right_on='Id')

    # Normalize to lowercase to avoid duplicates like 'Gender' vs 'gender'
    merged_keywords['Word'] = merged_keywords['Word'].str.lower()

    # Count keyword frequency
    keyword_counts = merged_keywords['Word'].value_counts()

    # Apply filters
    if search_term:
        keyword_counts = keyword_counts[keyword_counts.index.str.contains(search_term, case=False)]
    keyword_counts = keyword_counts[keyword_counts >= min_freq]

    # Show bar chart
    st.subheader("Top {} Keywords in Funded Research".format(top_n))
    if not keyword_counts.empty:
        st.bar_chart(keyword_counts.head(top_n))
    else:
        st.info("No keywords match the current filters.")

    # Word Cloud
    st.subheader(" Word Cloud of All Keywords")
    if not keyword_counts.empty:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(keyword_counts)
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)
    else:
        st.warning("️ Not enough keywords to generate a word cloud. Try changing your filters.")

# --------------------------- Placeholder Pages ---------------------------
elif page == "Diversity Insights":
    st.title(" Diversity Insights")

    # Sidebar Filters
    st.sidebar.markdown("###  Filters")
    gender_options = ["All"] + sorted(person_df["Gender"].dropna().unique())
    selected_gender = st.sidebar.selectbox("Select Gender:", gender_options)

    min_year = int(grant_df["CallDecisionYear"].min())
    max_year = int(grant_df["CallDecisionYear"].max())
    year_range = st.sidebar.slider("Select Year Range:", min_year, max_year, (min_year, max_year))

    min_funding = int(grant_df["AmountGrantedAllSets"].min())
    max_funding = int(grant_df["AmountGrantedAllSets"].max())
    funding_range = st.sidebar.slider("Total Funding (CHF) Range:", min_funding, max_funding, (min_funding, max_funding))

    # Merge Data
    merged = pd.merge(grant_to_person_df, grant_df[["GrantNumber", "AmountGrantedAllSets", "CallDecisionYear"]], on="GrantNumber")
    merged = pd.merge(merged, person_df[["PersonNumber", "Gender"]], on="PersonNumber")

    # Apply Filters
    filtered = merged[
        (merged["CallDecisionYear"] >= year_range[0]) &
        (merged["CallDecisionYear"] <= year_range[1]) &
        (merged["AmountGrantedAllSets"] >= funding_range[0]) &
        (merged["AmountGrantedAllSets"] <= funding_range[1])
    ]
    if selected_gender != "All":
        filtered = filtered[filtered["Gender"] == selected_gender]

    # Prepare Data
    gender_distribution = person_df["Gender"].value_counts()
    total_funding_by_gender = filtered.groupby("Gender")["AmountGrantedAllSets"].sum()
    yearly_gender_funding = filtered.groupby(["CallDecisionYear", "Gender"])["AmountGrantedAllSets"].sum().reset_index()

    # Charts in Tabs
    tab1, tab2, tab3 = st.tabs([" Gender Distribution", " Funding by Year and Gender", " Total Funding by Gender"])

    with tab1:
        st.subheader("1. Gender Distribution of Researchers")
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        ax1.pie(gender_distribution, labels=gender_distribution.index, autopct='%1.1f%%', startangle=90)
        ax1.axis("equal")
        st.pyplot(fig1)

    with tab2:
        st.subheader("2. Yearly Funding by Gender")
        fig2 = px.bar(
            yearly_gender_funding,
            x="CallDecisionYear",
            y="AmountGrantedAllSets",
            color="Gender",
            labels={"AmountGrantedAllSets": "Funding (CHF)", "CallDecisionYear": "Year"},
            title="Funding by Year and Gender"
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2)

    with tab3:
        st.subheader("3. Total Funding by Gender")
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        ax3.bar(total_funding_by_gender.index, total_funding_by_gender.values, color=["#1f77b4", "#ff7f0e"])
        ax3.set_ylabel("Total Funding (CHF)")
        st.pyplot(fig3)

# --------------------------- Collaboration Network ---------------------------
elif page == "Collaboration Network":
    st.title(" Collaboration Network")
    st.image("data/sna1.png", use_column_width=True)
    st.markdown("""
###  What does this graph show?

This network visualization highlights the **collaborations between the top 100 researchers** in the SNSF dataset. Each **node** represents a researcher, and each **line (edge)** between them indicates that they have **co-applied for at least one research grant**.

###  Key Observations:
- **Larger and darker nodes** indicate researchers with more collaborations (i.e., they are highly connected in the network).
- **Tightly clustered groups** represent **strong collaborative communities** or research teams.
- **Bridging nodes** connect two or more clusters, acting as **key intermediaries** between research groups.

###  Why is this important?
This type of Social Network Analysis helps to:
- **Identify key influencers** and central figures in the research ecosystem.
- Reveal **collaborative patterns**, helping decision-makers understand how interdisciplinary connections form.
- Support strategic planning by showcasing **collaboration strengths and gaps**.

###  Source:
The graph was generated using **Gephi** from the top 100 most collaborative researchers based on grant co-application records.
""")


# --------------------------- AI Insights ---------------------------
elif page == "AI Insights":
    st.title(" AI Research Insights")

    # --- Sidebar Filters ---
    st.sidebar.markdown("###  Filters")
    year_min, year_max = int(grant_df['CallDecisionYear'].min()), int(grant_df['CallDecisionYear'].max())
    year_range = st.sidebar.slider("Select Year Range:", min_value=year_min, max_value=year_max, value=(year_min, year_max))

    fund_min = int(grant_df['AmountGrantedAllSets'].min())
    fund_max = int(grant_df['AmountGrantedAllSets'].max())
    fund_range = st.sidebar.slider("Funding Amount (CHF):", min_value=fund_min, max_value=fund_max, value=(fund_min, fund_max))

    show_keywords = st.sidebar.checkbox(" Show Matched AI Keywords")

    # --- AI Keyword Matching ---
    ai_keywords = ["artificial intelligence", "machine learning", "deep learning", "neural network", "neural networks"]
    keyword_df['Word'] = keyword_df['Word'].astype(str).str.lower()

    # Match AI keywords
    ai_keyword_ids = keyword_df[keyword_df['Word'].str.contains('|'.join(ai_keywords), na=False)]['Id'].unique()

    if show_keywords:
        st.subheader(" Matched AI Keywords")
        st.dataframe(keyword_df[keyword_df['Id'].isin(ai_keyword_ids)][['Id', 'Word']])

    # Find grant numbers that have those AI keyword IDs
    ai_grant_ids = grant_keyword_df[grant_keyword_df['KeywordId'].isin(ai_keyword_ids)]['GrantNumber'].unique()

    # Fix mismatched GrantNumber formats
    grant_df['GrantNumberNumeric'] = grant_df['GrantNumber'].str.extract(r'(\d+)').astype(int)

    # Match AI grants
    ai_grants = grant_df[grant_df['GrantNumberNumeric'].isin(ai_grant_ids)].copy()

    if ai_grants.empty:
        st.warning(" No AI-related grants found.")
    else:
        # Apply filters
        ai_grants = ai_grants.dropna(subset=['CallDecisionYear', 'AmountGrantedAllSets'])
        ai_grants['CallDecisionYear'] = ai_grants['CallDecisionYear'].astype(int)
        ai_grants = ai_grants[
            (ai_grants['CallDecisionYear'] >= year_range[0]) &
            (ai_grants['CallDecisionYear'] <= year_range[1]) &
            (ai_grants['AmountGrantedAllSets'] >= fund_range[0]) &
            (ai_grants['AmountGrantedAllSets'] <= fund_range[1])
        ]

        st.subheader(f" Total AI Grants Found: {len(ai_grants)}")

        # --- Chart 1: AI Funding Over Time ---
        st.subheader(" AI Funding Over Time")
        funding_trend = ai_grants.groupby("CallDecisionYear")["AmountGrantedAllSets"].sum().reset_index()
        fig1 = px.line(funding_trend, x="CallDecisionYear", y="AmountGrantedAllSets",
                       labels={"CallDecisionYear": "Year", "AmountGrantedAllSets": "Funding (CHF)"},
                       markers=True)
        st.plotly_chart(fig1, use_container_width=True)

        # --- Chart 2: Top AI Researchers by Funding ---
        st.subheader(" Top AI Researchers by Total AI Funding")
        ai_grant_people = grant_to_person_df[grant_to_person_df['GrantNumber'].isin(ai_grants['GrantNumber'])]
        merged = pd.merge(ai_grant_people, ai_grants[['GrantNumber', 'AmountGrantedAllSets']], on='GrantNumber')
        merged = pd.merge(merged, person_df[['PersonNumber', 'FirstName', 'Surname']], on='PersonNumber')
        merged['FullName'] = merged['FirstName'] + ' ' + merged['Surname']
        top_ai_researchers = merged.groupby('FullName')['AmountGrantedAllSets'].sum().nlargest(10).reset_index()
        fig2 = px.bar(top_ai_researchers, x='FullName', y='AmountGrantedAllSets',
                      labels={"FullName": "Researcher", "AmountGrantedAllSets": "Total AI Funding (CHF)"},
                      title="Top 10 AI Researchers")
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)




