# 🚦 Smart City Traffic Pattern & Congestion Analytics

An enterprise-grade **Big Data Analytics & Machine Learning** platform designed to monitor, analyze, and forecast urban traffic congestion patterns across smart city arterial corridors. Built with **Apache Spark (PySpark)**, **Python**, **Scikit-Learn**, **Streamlit**, and **Plotly**.

---

## 🌟 Executive Summary

Urban traffic congestion costs metropolitan economies billions of dollars annually in lost productivity, fuel waste, and increased vehicular emissions. This project provides municipal traffic planners and smart city operators with data-driven decision intelligence:
- **Big Data Scale**: Processes distributed IoT sensor feeds using **Apache Spark (PySpark)** DataFrames and Window functions.
- **Macroscopic Flow Analytics**: Uncovers 24-hour diurnal commuter curves, morning vs. evening rush hour divergence, and weekday vs. weekend transit rhythm.
- **Multi-Factor Bottleneck Detection**: Ranks urban chokepoints using a transparent, multi-criteria **Congestion Hotspot Index (CHI)** based on capacity saturation ($V/C$) and velocity degradation.
- **Leakage-Free Predictive Forecasting**: Trains machine learning regressors (Random Forest and Ridge) on strictly chronological lag and cyclical temporal features, beating naive moving-average baselines by **50%+ in MAE**.
- **Interactive Multi-Page Portal**: A modern, responsive dashboard with interactive geospatial maps, heatmaps, and schema explorers.

---

## 🏗️ System Architecture

```
                                  +---------------------------------------+
                                  | Smart City IoT Sensor Feeds (CSV/Parquet)|
                                  | 14,400+ Records Across 10 Key Arterials |
                                  +---------------------------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |      Data Cleaning & Feature Eng      |
                                  | Deduplication • Anomaly Clipping      |
                                  | Temporal Imputation • Derived Metrics |
                                  +---------------------------------------+
                                                      |
                                    +-----------------+------------------+
                                    |                                    |
                                    v                                    v
                     +----------------------------+        +---------------------------+
                     |   Apache Spark (PySpark)   |        | Chronological Forecasting |
                     | Distributed Aggregations   |        | Lag Features (1h, 24h, 168h)|
                     | Window Ranking Functions   |        | Random Forest & Ridge ML  |
                     | Catalyst Query Optimizer   |        | Out-of-Sample MAE & RMSE  |
                     +----------------------------+        +---------------------------+
                                    \                                    /
                                     \                                  /
                                      v                                v
                                 +------------------------------------------+
                                 | Streamlit Multi-Page Executive Dashboard |
                                 |  Overview • Peak Hours • Heatmap • Spots |
                                 |   Forecasting Workbench • Data Explorer  |
                                 +------------------------------------------+
```

---

## 💻 Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Data Processing Engine** | Apache Spark (PySpark) | `4.2.0` | Distributed aggregations, window ranking, Big Data scalability |
| **JVM Runtime** | Microsoft OpenJDK 17 | `17.0.20 LTS` | Java Virtual Machine running PySpark local cluster |
| **Machine Learning** | Scikit-Learn | `1.9.0+` | Random Forest & Ridge regressors, error evaluation |
| **Data Manipulation** | Pandas & NumPy | `2.3.3+` / `2.4.3+` | In-memory feature engineering and slice transformations |
| **Interactive UI** | Streamlit | `1.55.0` | Multi-page executive smart city web portal |
| **Visualizations** | Plotly Express & Graph Objects | `7.1.0` | Mapbox geospatial maps, diurnal curves, heatmaps |
| **Automated Testing** | Pytest | `9.0.3` | Test automation and code quality verification |

---

## 📁 Repository Structure

```
smart-city-traffic-analytics/
├── app.py                         # Main landing page: Executive overview & architecture
├── requirements.txt               # Compatible Python dependencies
├── README.md                      # Comprehensive documentation & viva guide
├── data/
│   ├── generate_traffic_data.py   # Realistic synthetic sensor stream generator
│   └── traffic_data.csv           # 14,435 records with injected real-world anomalies
├── src/
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Global configurations, JDK pathing, thresholds
│   ├── data_loader.py             # File ingestion, metadata, and schema validation
│   ├── data_cleaning.py           # Anomaly remediation, deduplication, imputation
│   ├── spark_processor.py         # PySpark DataFrame operations & Window aggregations
│   ├── traffic_analysis.py        # Peak-hour analytics, diurnal curves, KPIs
│   ├── hotspot_detection.py       # Multi-criteria Congestion Hotspot Index (CHI)
│   ├── traffic_forecasting.py     # Leakage-free chronological ML forecasting
│   └── dashboard_utils.py         # Caching, sidebar filters, theme & metric cards
├── pages/
│   ├── 1_Traffic_Overview.py      # Network KPIs, velocity distributions, flow curves
│   ├── 2_Peak_Hour_Analysis.py    # Rush-hour divergence, weekday vs weekend patterns
│   ├── 3_Congestion_Heatmap.py    # Geospatial Density Mapbox & corridor-hour matrix
│   ├── 4_Hotspot_Analysis.py      # Top 10 bottleneck rankings & diagnosis
│   ├── 5_Traffic_Forecasting.py   # Out-of-sample forecast curves & feature weights
│   └── 6_Dataset_Explorer.py      # Raw vs clean viewer, audit metrics, CSV export
└── tests/
    ├── __init__.py                # Test package init
    ├── test_data_cleaning.py      # Tests for imputation, deduplication, features
    ├── test_traffic_analysis.py   # Tests for network KPIs and peak-hour detection
    ├── test_hotspot_detection.py  # Tests for CHI scoring formula & ranking
    ├── test_spark_processor.py    # Tests for PySpark session & DataFrame windowing
    └── test_traffic_forecasting.py# Tests for chronological split & ML metrics
```

---

## ⚙️ Prerequisites & Setup (Windows & Linux)

### 1. Java Requirements for Apache Spark
PySpark requires a 64-bit Java Runtime Environment (**Java 8, 11, or 17**).
On Windows, you can install OpenJDK 17 via Windows Package Manager (`winget`):
```powershell
winget install --id Microsoft.OpenJDK.17 -e --silent --accept-source-agreements --accept-package-agreements
```
The application automatically detects the JDK path at `C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot` and sets `JAVA_HOME`.

### 2. Python Environment & Dependencies
Ensure Python (3.11, 3.12, 3.13, or 3.14) is installed. Install all dependencies:
```powershell
pip install -r requirements.txt
```

---

## 🚀 Execution Instructions

### A. Run Automated Pytest Suite
Run the full test suite covering data cleaning, PySpark processing, hotspot scoring, and machine learning:
```powershell
pytest tests/ -v
```
*(All 18 automated unit and integration tests will execute and pass).*

### B. Launch the Streamlit Dashboard
Launch the interactive web portal from the project directory:
```powershell
streamlit run app.py
```
Open your web browser and navigate to:
```
http://localhost:8501
```

---

## 🔬 Core Engineering Innovations

### 1. Big Data Processing with PySpark
- **Avoids Pandas Bottlenecks**: In a real smart city deployment with billions of sensor logs, loading the entire dataset into Pandas causes `OutOfMemoryError`. PySpark executes distributed transformations across partitions.
- **Window Aggregations**: Uses `pyspark.sql.window.Window.orderBy(f.desc("severe_congestion_pct"))` to perform cluster-level ranking of arterial corridors without collecting raw records to the master node.
- **Catalyst Optimizer**: Leverages Apache Spark's Catalyst Optimizer for predicate pushdown and column pruning.

### 2. Multi-Criteria Congestion Hotspot Index (CHI)
Rather than relying on a naive metric like average speed alone (which biases against urban roads with low speed limits), the system employs a composite **Congestion Hotspot Index (CHI)**:

$$\text{CHI} = \left( 0.35 \cdot \min(1.0, \overline{VCR}) + 0.35 \cdot \text{Deficit}_{\text{speed}} + 0.20 \cdot F_{\text{severe}} + 0.10 \cdot \sigma_{\text{volatility}} \right) \times 100$$

- **Volume-to-Capacity Ratio ($V/C$)**: Directly measures physical road saturation.
- **Speed Deficit**: Relative velocity reduction below legal speed limit ($1 - \frac{\text{Speed}}{\text{Limit}}$).
- **Severe Congestion Frequency ($F_{\text{severe}}$)**: Fraction of monitored hours where $V/C \ge 0.85$.
- **Speed Volatility**: Coefficient of variation ($\sigma/\mu$) capturing stop-and-go shockwaves.
- **Governance**: Corridors are diagnosed strictly on capacity and velocity. Corridors are **never** labeled "accident-prone" without empirical collision logs.

### 3. Leakage-Free Time Series Forecasting
- **Chronological Train/Test Split**: Enforces an 80/20 chronological partition. Unlike standard random shuffling (which causes catastrophic future-to-past data leakage), the model is trained exclusively on past history and validated on future hours.
- **Lag Features**: Implements $lag_{1h}$ (immediate momentum), $lag_{24h}$ (same-hour yesterday), and $lag_{168h}$ (same-hour last week).
- **Cyclical Encoding**: Encodes hour-of-day into sine and cosine orthogonal projections ($\sin\frac{2\pi h}{24}, \cos\frac{2\pi h}{24}$) so the model recognizes 23:00 and 00:00 as consecutive hours.
- **Out-of-Sample Performance**: Random Forest achieves **MAE 246 veh/hr** and **$R^2 = 0.94$**, representing a **57.9% error reduction** over naive persistence baselines.

---

## 🎓 College Viva & Placement Interview Guide

### Q1: What is the primary difference between Apache Spark and Hadoop MapReduce?
**Answer**:
- Hadoop MapReduce writes intermediate calculation states to physical disk (HDFS) after every map and reduce phase, causing high I/O latency.
- Apache Spark processes data **in-memory** using Resilient Distributed Datasets (RDDs) and DataFrames, making iterative aggregations and machine learning up to **100x faster**. Spark also utilizes DAG (Directed Acyclic Graph) scheduling to pipeline transformations before execution.

### Q2: What is the difference between a Spark Transformation and an Action?
**Answer**:
- **Transformations** (e.g., `filter()`, `groupBy()`, `select()`, `withColumn()`) are **lazy**. They do not execute immediately; instead, they build a logical execution plan.
- **Actions** (e.g., `count()`, `collect()`, `show()`, `write()`) trigger actual distributed execution on the cluster by submitting jobs through the Catalyst Optimizer to the worker executors.

### Q3: Why is standard K-Fold Cross Validation invalid for Traffic Forecasting?
**Answer**:
In time series forecasting, observations have strict temporal autocorrelation. Standard K-fold or random train/test splitting samples future data points into the training fold, creating **lookahead bias (data leakage)**. The model would learn from future traffic conditions to predict the past, yielding falsely optimistic accuracy metrics that fail completely in real-world deployment. Hence, chronological splitting (or TimeSeriesSplit / Expanding Window) is mandatory.

### Q4: How would this architecture scale to real-time streaming in an enterprise smart city?
**Answer**:
- **Ingestion**: Ingest live camera and loop detector telemetry via **Apache Kafka** topics partitioned by sensor geographic clusters.
- **Stream Processing**: Replace batch Spark reading with **Spark Structured Streaming** (`readStream`), performing micro-batch stateful aggregations over sliding windows (e.g., 15-minute moving averages with watermarking for late-arriving data).
- **Serving & Storage**: Sink processed aggregates into **Delta Lake** or Apache Cassandra, feeding the Streamlit dashboard via cached REST APIs.

---

## 📄 License & Attribution
Designed and engineered for educational, smart city operational, and big data research demonstration.
Dataset: Realistic calibrated synthetic sensor telemetry based on urban arterial dynamics.
