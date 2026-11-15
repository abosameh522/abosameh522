# Ahmed Sameh

**Data Engineer** — batch pipelines, dimensional modeling, and data quality in Python and SQL.

I build data platforms end to end: Bronze/Silver/Gold lakes in Parquet, Prefect-orchestrated flows, Pandera schema gates that fail a run instead of a dashboard, and star schemas in PostgreSQL. My projects ship with tests, containers, and honest evaluation rather than a notebook that only runs once.

CS & AI at Mansoura University (2027). Open to Data Engineer and Data Analyst roles in Egypt and remote.

<br>

## Stack

| Layer | Tools |
| :--- | :--- |
| **Orchestration** | Prefect, Python |
| **Storage & Lakehouse** | Parquet, DuckDB, Bronze/Silver/Gold layering |
| **Modeling & Warehouse** | PostgreSQL, dimensional star schemas, SQL |
| **Transformation** | pandas, NumPy, DuckDB SQL |
| **Data Quality** | Pandera, pytest, DuckDB aggregate checks |
| **Serving** | FastAPI, Streamlit |
| **Platform & Tooling** | Docker, Docker Compose, GitHub Actions, uv, Ruff, Git |

<br>

## Featured project

### [Nile Delta Crop Monitoring System](https://github.com/abosameh522/delta-crop-monitoring-system)

An end-to-end satellite data pipeline over a 50×50 km AOI in the Nile Delta, covering six seasons from 2019 to 2024.

- **Ingestion** — Sentinel-2 L2A scenes via STAC search plus Open-Meteo daily weather, landed unchanged as Bronze.
- **Transformation** — clipping, CRS unification, cloud masking, and NDVI computed into one Silver file per acquisition date; weather rolled up to weekly Gold with anomaly detection.
- **Quality gates** — Pandera schemas and DuckDB aggregates run between layers and exit non-zero on a critical failure, so bad data never reaches Gold.
- **Modeling** — an XGBoost crop-stress model evaluated with a time-based split and a spatially held-out region, against honest baselines.
- **Serving** — a read-only Streamlit dashboard over the Gold layer.
- **Reproducibility** — Prefect flows, Docker Compose, and a committed demo sample that runs without the 31 GB lake.

`Python` · `Prefect` · `DuckDB` · `Parquet` · `Pandera` · `Docker` · `XGBoost` · `Streamlit`

<br>

## Other projects

| Project | What it is | Stack |
| :--- | :--- | :--- |
| **[E-commerce Data Pipeline](https://github.com/abosameh522/ecommerce-data-pipeline)** | Batch ETL from Olist CSVs into an idempotent PostgreSQL star schema, with a data-quality checks table and 28 tests across unit and integration suites | Python, PostgreSQL, Docker Compose, pytest, Ruff |
| **[Phishing URL Detection](https://github.com/abosameh522/phishing-url-detection)** | URL-only classifier with leakage-resistant domain splits, served behind a FastAPI service and a Streamlit UI | Python, scikit-learn, FastAPI, Streamlit |
| **[Customer Churn Prediction](https://github.com/abosameh522/customer-churn-prediction)** | Churn models tuned for retention economics, where the decision threshold is chosen from offer cost against lost revenue | Python, scikit-learn, pandas |
| **[Credit Risk Analysis](https://github.com/abosameh522/credit-risk-analysis)** | Loan-default classification with nested cross-validation and a cost-based probability threshold | Python, scikit-learn, pandas |

<br>

## Contact

[![Email](https://img.shields.io/badge/Email-abosameh1342005%40gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:abosameh1342005@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-ahmed--sameh--283927414-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ahmed-sameh-283927414)
[![GitHub](https://img.shields.io/badge/GitHub-%40abosameh522-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/abosameh522)
