import ast
import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="WikiLens",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main {background-color: #0e1117;}
[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #30363d;
    padding: 14px;
    border-radius: 12px;
}
.article-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


DATA_PATHS = [
    Path("data/enwiki_namespace_0_00003.parquet"),
    Path("enwiki_namespace_0_00003.parquet"),
]


def find_data_file():
    for path in DATA_PATHS:
        if path.exists():
            return path
    return None


@st.cache_data
def load_data(path):
    df = pd.read_parquet(path)
    for col in ["name", "abstract", "description", "url", "sections", "infoboxes", "image"]:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("")
    df["name"] = df["name"].astype(str)
    df["abstract"] = df["abstract"].astype(str)
    return df


def parse_value(value):
    if value is None or value == "":
        return None
    if isinstance(value, (dict, list)):
        return value

    text = str(value)

    for parser in (json.loads, ast.literal_eval):
        try:
            return parser(text)
        except Exception:
            pass

    return text


def count_items(value):
    parsed = parse_value(value)
    if isinstance(parsed, dict):
        return len(parsed)
    if isinstance(parsed, list):
        return len(parsed)
    if parsed:
        return 1
    return 0


def show_sections(value):
    parsed = parse_value(value)

    if isinstance(parsed, dict):
        for title, content in parsed.items():
            st.markdown(f"#### {title}")
            st.write(content)

    elif isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict):
                title = item.get("title") or item.get("name") or "Section"
                content = item.get("text") or item.get("content") or item
                st.markdown(f"#### {title}")
                st.write(content)
            else:
                st.write(item)
    elif parsed:
        st.write(parsed)
    else:
        st.info("No structured sections available for this article.")


data_file = find_data_file()

if data_file is None:
    st.error("Dataset not found.")
    st.markdown("""
### Put the dataset here

Create this folder:

`data/`

Then place:

`enwiki_namespace_0_00003.parquet`

inside it.

The application expects the Wikimedia structured Wikipedia dataset used by this project.
""")
    st.stop()

df = load_data(data_file)

st.title("🌍 WikiLens")
st.caption("Explore structured Wikipedia knowledge with fast search, article insights and visual statistics.")

with st.sidebar:
    st.header("🔎 Search")

    query = st.text_input("Search articles", placeholder="Try India, Python, Space...")

    st.divider()
    st.header("📊 Filters")

    min_words = st.slider("Minimum abstract words", 0, 1000, 0, 50)

    st.divider()
    st.caption(f"Dataset: {len(df):,} articles")
    st.caption("Built with Python + Pandas + Streamlit")

filtered = df.copy()

if query.strip():
    q = query.strip().lower()
    mask = (
        filtered["name"].str.lower().str.contains(q, na=False)
        | filtered["abstract"].str.lower().str.contains(q, na=False)
        | filtered["description"].str.lower().str.contains(q, na=False)
    )
    filtered = filtered[mask]

filtered["abstract_words"] = filtered["abstract"].str.split().str.len()
filtered = filtered[filtered["abstract_words"] >= min_words]

tab1, tab2, tab3 = st.tabs(["🔍 Search", "📈 Dataset Analytics", "ℹ️ About"])

with tab1:
    if not query.strip():
        st.info("Enter a topic in the search box to explore the dataset.")

        st.subheader("✨ Example topics")
        cols = st.columns(4)
        examples = ["India", "Python", "Artificial intelligence", "Space"]
        for col, example in zip(cols, examples):
            col.write(f"**{example}**")
    else:
        st.subheader(f"Search results for: `{query}`")
        st.write(f"Found **{len(filtered):,}** matching article(s).")

        if filtered.empty:
            st.warning("No matching article was found.")
        else:
            for idx, row in filtered.head(20).iterrows():
                with st.container(border=True):
                    st.markdown(f"### {row['name']}")

                    if row["description"]:
                        st.caption(str(row["description"]))

                    abstract = str(row["abstract"]).strip()
                    if abstract:
                        st.write(abstract[:900] + ("..." if len(abstract) > 900 else ""))
                    else:
                        st.write("No abstract available.")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Abstract words", f"{row['abstract_words']:,}")
                    c2.metric("Sections", count_items(row["sections"]))
                    c3.metric("Images", count_items(row["image"]))

                    with st.expander("📚 Explore article"):
                        st.markdown("#### Sections")
                        show_sections(row["sections"])

                        st.markdown("#### 📦 Infobox")
                        infobox = parse_value(row["infoboxes"])
                        if isinstance(infobox, dict):
                            st.json(infobox)
                        elif infobox:
                            st.write(infobox)
                        else:
                            st.info("No structured infobox available.")

                        if row["url"]:
                            st.link_button("🌐 Open Wikipedia article", str(row["url"]))

with tab2:
    st.subheader("Dataset Overview")

    total_articles = len(df)
    avg_words = df["abstract"].str.split().str.len().mean()
    total_sections = df["sections"].apply(count_items).sum()
    total_images = df["image"].apply(count_items).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Articles", f"{total_articles:,}")
    c2.metric("Avg. abstract words", f"{avg_words:,.0f}")
    c3.metric("Sections", f"{total_sections:,}")
    c4.metric("Images", f"{total_images:,}")

    st.subheader("Article richness")

    analytics = pd.DataFrame({
        "Metric": ["Articles", "Articles with images", "Articles with sections", "Articles with infoboxes"],
        "Count": [
            len(df),
            int((df["image"].apply(count_items) > 0).sum()),
            int((df["sections"].apply(count_items) > 0).sum()),
            int((df["infoboxes"].apply(count_items) > 0).sum()),
        ],
    })

    st.bar_chart(analytics.set_index("Metric"))

    st.subheader("Longest abstracts")
    longest = df.assign(
        words=df["abstract"].str.split().str.len()
    ).nlargest(10, "words")[["name", "words"]]
    st.dataframe(longest, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("About WikiLens")

    st.write("""
    WikiLens is a student-built knowledge explorer powered by a structured
    Wikimedia Wikipedia dataset.

    The project demonstrates:
    - Fast article search
    - Structured article exploration
    - Dataset analytics
    - Image, section and infobox inspection
    - Interactive dark-mode-friendly UI
    - Git/GitHub collaboration
    """)

    st.markdown("### 🛠 Technology")
    st.code("Python\nPandas\nPyArrow\nStreamlit\nGit\nGitHub")
