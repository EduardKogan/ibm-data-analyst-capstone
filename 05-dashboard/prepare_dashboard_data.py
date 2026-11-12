"""
Prepare tidy CSVs for the Looker Studio dashboard (Module 5, Lab 26).

Looker Studio cannot split multi-select survey answers ("Python;SQL;Bash"),
so the reshaping is done here in pandas and each chart gets its own small,
pre-aggregated CSV in ./dashboard_data/.

Run:  python prepare_dashboard_data.py
"""
from pathlib import Path

import pandas as pd

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "HLOosvsPgIwt5dgOOh1RSg/survey-data-updated.csv")
OUT = Path(__file__).parent / "dashboard_data"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(URL)
print(f"Loaded {len(df):,} respondents")


def tech_counts(col: str, name: str, n: int = 10) -> pd.DataFrame:
    """Split a ';'-separated column, count each technology, keep the top n."""
    out = (df[col].dropna().str.split(";").explode().str.strip()
             .value_counts().head(n)
             .rename_axis("Technology").reset_index(name="Count"))
    out["Rank"] = range(1, len(out) + 1)
    out.to_csv(OUT / f"{name}.csv", index=False)
    return out


# Pages 1 and 2: current vs. desired technology (top 10 each)
tech_counts("LanguageHaveWorkedWith", "01_languages_current")
tech_counts("DatabaseHaveWorkedWith", "02_databases_current")
tech_counts("PlatformHaveWorkedWith", "03_platforms_current")
tech_counts("WebframeHaveWorkedWith", "04_webframes_current")
tech_counts("LanguageWantToWorkWith", "05_languages_future")
tech_counts("DatabaseWantToWorkWith", "06_databases_future")
tech_counts("PlatformWantToWorkWith", "07_platforms_future")
tech_counts("WebframeWantToWorkWith", "08_webframes_future")

# Page 3: demographics
countries = (df["Country"].replace({
                 "United States of America": "United States",
                 "United Kingdom of Great Britain and Northern Ireland": "United Kingdom"})
               .value_counts().rename_axis("Country").reset_index(name="Count"))
countries.to_csv(OUT / "09_countries.csv", index=False)

age_order = ["Under 18 years old", "18-24 years old", "25-34 years old",
             "35-44 years old", "45-54 years old", "55-64 years old",
             "65 years or older", "Prefer not to say"]
sort_order = {age: i for i, age in enumerate(age_order, start=1)}

ages = df["Age"].value_counts().rename_axis("Age").reset_index(name="Count")
ages["SortOrder"] = ages["Age"].map(sort_order)
ages.sort_values("SortOrder").to_csv(OUT / "10_age_groups.csv", index=False)

df["EdLevel"] = df["EdLevel"].str.split(" \\(").str[0]  # shorten long labels
edu = df["EdLevel"].value_counts().rename_axis("EdLevel").reset_index(name="Count")
edu["Percent"] = (edu["Count"] / edu["Count"].sum() * 100).round(1)
edu.to_csv(OUT / "11_education.csv", index=False)

age_edu = (df.dropna(subset=["Age", "EdLevel"])
             .groupby(["Age", "EdLevel"]).size().reset_index(name="Count"))
age_edu["SortOrder"] = age_edu["Age"].map(sort_order)
age_edu.sort_values(["SortOrder", "EdLevel"]).to_csv(OUT / "12_age_by_education.csv", index=False)

print(f"Wrote 12 files to {OUT}")
