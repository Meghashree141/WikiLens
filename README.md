# 🌍 WikiLens

**AI-ready Wikipedia Knowledge Explorer built with the Wikimedia Structured Wikipedia Dataset.**

WikiLens is a student project that turns structured Wikipedia data into an interactive knowledge explorer.

## Features

- 🔍 Fast article search
- 📝 Article abstracts and descriptions
- 📚 Structured article sections
- 📦 Infobox exploration
- 🖼 Image metadata
- 📊 Dataset analytics
- 🌙 Dark-mode-friendly interface
- 🔗 Direct Wikipedia article links
- 🤝 Git/GitHub collaboration ready

## Tech Stack

- Python
- Pandas
- PyArrow
- Streamlit
- Git
- GitHub

## Project Structure

```text
WikiLens/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── enwiki_namespace_0_00003.parquet
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/WikiLens.git
cd WikiLens
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the dataset

Put:

```text
enwiki_namespace_0_00003.parquet
```

inside:

```text
data/
```

### 5. Run

```bash
streamlit run app.py
```

## Team Git Workflow

Each member should work on a separate branch.

```bash
git checkout -b feature-search
```

After making changes:

```bash
git add .
git commit -m "Add article search"
git push -u origin feature-search
```

Then open a Pull Request on GitHub and merge it after review.

## Important

Do not commit very large dataset files unless the team has decided to use Git LFS or another dataset-hosting method.

Every team member should understand the code they contribute.

## Future AI Features

Possible extensions:

- Semantic search
- RAG question answering
- AI article summarization
- Quiz generation
- Multilingual comparison
- Knowledge graph
- Article recommendation
