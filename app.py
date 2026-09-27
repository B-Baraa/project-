import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Retail Sales 2024 | Big Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "retail_sales_2024.csv"

# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #f7f9fc;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .dashboard-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.15rem;
        }

        .dashboard-subtitle {
            color: #64748b;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: white;
            padding: 1rem 1.1rem;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            min-height: 105px;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 650;
            margin-top: 0.8rem;
            margin-bottom: 0.5rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid #e5e7eb;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """Load and prepare the exact retail_sales_2024.csv dataset."""
    df = pd.read_csv(file_path)

    # Exact project schema
    expected_columns = [
        "order_id",
        "date",
        "category",
        "region",
        "channel",
        "payment_method",
        "quantity",
        "unit_price",
        "customer_age",
        "rating",
        "total_amount",
    ]

    missing = [c for c in expected_columns if c not in df.columns]
    if missing:
        raise ValueError(
            "Colonnes manquantes dans le dataset : " + ", ".join(missing)
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["month_name"] = df["date"].dt.strftime("%b")
    df["year"] = df["date"].dt.year

    return df


# ============================================================
# HELPERS
# ============================================================

def money(value: float) -> str:
    return f"{value:,.2f} TND".replace(",", " ")


def pct(value: float) -> str:
    return f"{value:.1f}%"


def make_download(df: pd.DataFrame, filename: str) -> None:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Télécharger les données filtrées",
        data=csv,
        file_name=filename,
        mime="text/csv",
    )


# ============================================================
# LOAD DATA
# ============================================================

if not DATA_FILE.exists():
    st.error(
        "Le fichier `retail_sales_2024.csv` est introuvable. "
        "Placez `app.py` et `retail_sales_2024.csv` dans le même dossier."
    )
    st.stop()

try:
    df = load_data(str(DATA_FILE))
except Exception as exc:
    st.error(f"Impossible de charger le dataset : {exc}")
    st.stop()

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("🎛️ Filtres")

st.sidebar.caption("Retail Sales 2024 — Projet Big Data")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Période",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

regions = st.sidebar.multiselect(
    "Région",
    options=sorted(df["region"].dropna().unique()),
    default=sorted(df["region"].dropna().unique()),
)

categories = st.sidebar.multiselect(
    "Catégorie",
    options=sorted(df["category"].dropna().unique()),
    default=sorted(df["category"].dropna().unique()),
)

channels = st.sidebar.multiselect(
    "Canal",
    options=sorted(df["channel"].dropna().unique()),
    default=sorted(df["channel"].dropna().unique()),
)

payments = st.sidebar.multiselect(
    "Moyen de paiement",
    options=sorted(df["payment_method"].dropna().unique()),
    default=sorted(df["payment_method"].dropna().unique()),
)

# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df[
    (df["date"].dt.date >= start_date)
    & (df["date"].dt.date <= end_date)
    & (df["region"].isin(regions))
    & (df["category"].isin(categories))
    & (df["channel"].isin(channels))
    & (df["payment_method"].isin(payments))
].copy()

if filtered.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">📊 Retail Sales 2024 — Big Data Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dashboard-subtitle">'
    "Analyse interactive des ventes retail en Tunisie — "
    "PySpark / HDFS simulé / visualisation analytique"
    "</div>",
    unsafe_allow_html=True,
)

# ============================================================
# KPI CARDS
# ============================================================

total_revenue = filtered["total_amount"].sum()
orders = filtered["order_id"].nunique()
avg_basket = filtered["total_amount"].mean()
quantity = filtered["quantity"].sum()
avg_rating = filtered["rating"].mean()

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("💰 Chiffre d'affaires", money(total_revenue))
k2.metric("🧾 Commandes", f"{orders:,}".replace(",", " "))
k3.metric("🛒 Panier moyen", money(avg_basket))
k4.metric("📦 Quantités vendues", f"{quantity:,}".replace(",", " "))
k5.metric("⭐ Note moyenne", f"{avg_rating:.2f}/5")

st.caption(
    f"Affichage de {len(filtered):,} lignes sur {len(df):,} lignes du dataset."
    .replace(",", " ")
)

# ============================================================
# TABS
# ============================================================

tab_overview, tab_sales, tab_customers, tab_regions, tab_bigdata, tab_data = st.tabs(
    [
        "🏠 Vue d'ensemble",
        "📈 Analyse des ventes",
        "👥 Clients & paiements",
        "🌍 Régions",
        "⚙️ Big Data / Spark",
        "🗃️ Données",
    ]
)

# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tab_overview:
    st.markdown("<div class=\"section-title\">Évolution du chiffre d'affaires</div>",
                unsafe_allow_html=True)

    monthly = (
        filtered.groupby("month", as_index=False)
        .agg(
            chiffre_affaires=("total_amount", "sum"),
            commandes=("order_id", "nunique"),
        )
        .sort_values("month")
    )

    fig_month = px.line(
        monthly,
        x="month",
        y="chiffre_affaires",
        markers=True,
        labels={
            "month": "Mois",
            "chiffre_affaires": "Chiffre d'affaires (TND)",
        },
        title="Chiffre d'affaires mensuel",
    )
    fig_month.update_layout(
        hovermode="x unified",
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig_month, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        cat = (
            filtered.groupby("category", as_index=False)
            .agg(chiffre_affaires=("total_amount", "sum"))
            .sort_values("chiffre_affaires", ascending=False)
        )

        fig_cat = px.bar(
            cat,
            x="chiffre_affaires",
            y="category",
            orientation="h",
            labels={
                "chiffre_affaires": "CA (TND)",
                "category": "Catégorie",
            },
            title="CA par catégorie",
        )
        fig_cat.update_layout(height=400)
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        region = (
            filtered.groupby("region", as_index=False)
            .agg(chiffre_affaires=("total_amount", "sum"))
            .sort_values("chiffre_affaires", ascending=False)
        )

        fig_region = px.bar(
            region,
            x="region",
            y="chiffre_affaires",
            labels={
                "region": "Région",
                "chiffre_affaires": "CA (TND)",
            },
            title="CA par région",
        )
        fig_region.update_layout(height=400)
        st.plotly_chart(fig_region, use_container_width=True)

# ============================================================
# TAB 2 — SALES ANALYSIS
# ============================================================

with tab_sales:
    st.markdown('<div class="section-title">Analyse détaillée des ventes</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        cat_stats = (
            filtered.groupby("category", as_index=False)
            .agg(
                nb_commandes=("order_id", "nunique"),
                chiffre_affaires=("total_amount", "sum"),
                panier_moyen=("total_amount", "mean"),
                quantite=("quantity", "sum"),
            )
            .sort_values("chiffre_affaires", ascending=False)
        )

        fig = px.bar(
            cat_stats,
            x="category",
            y="chiffre_affaires",
            text_auto=".2s",
            labels={
                "category": "Catégorie",
                "chiffre_affaires": "CA (TND)",
            },
            title="Chiffre d'affaires par catégorie",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        channel_stats = (
            filtered.groupby("channel", as_index=False)
            .agg(
                chiffre_affaires=("total_amount", "sum"),
                nb_commandes=("order_id", "nunique"),
            )
        )

        fig = px.pie(
            channel_stats,
            names="channel",
            values="chiffre_affaires",
            hole=0.45,
            title="Répartition du CA par canal",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Canal × région")

    channel_region = (
        filtered.groupby(["region", "channel"], as_index=False)
        .agg(
            chiffre_affaires=("total_amount", "sum"),
            nb_commandes=("order_id", "nunique"),
        )
    )

    fig = px.bar(
        channel_region,
        x="region",
        y="chiffre_affaires",
        color="channel",
        barmode="group",
        labels={
            "region": "Région",
            "chiffre_affaires": "CA (TND)",
            "channel": "Canal",
        },
        title="CA par région et canal",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Tableau des performances par catégorie")
    st.dataframe(
        cat_stats.style.format(
            {
                "chiffre_affaires": "{:,.2f} TND",
                "panier_moyen": "{:,.2f} TND",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# TAB 3 — CUSTOMERS & PAYMENTS
# ============================================================

with tab_customers:
    st.markdown(
        '<div class="section-title">Clients, paiements et satisfaction</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        payment_stats = (
            filtered.groupby("payment_method", as_index=False)
            .agg(
                nb_commandes=("order_id", "nunique"),
                note_moyenne=("rating", "mean"),
                chiffre_affaires=("total_amount", "sum"),
            )
            .sort_values("nb_commandes", ascending=False)
        )

        fig = px.bar(
            payment_stats,
            x="payment_method",
            y="nb_commandes",
            text_auto=True,
            labels={
                "payment_method": "Moyen de paiement",
                "nb_commandes": "Nombre de commandes",
            },
            title="Nombre de commandes par moyen de paiement",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            payment_stats,
            x="payment_method",
            y="note_moyenne",
            text_auto=".2f",
            labels={
                "payment_method": "Moyen de paiement",
                "note_moyenne": "Note moyenne",
            },
            title="Note moyenne par moyen de paiement",
        )
        fig.update_yaxes(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        age_data = (
            filtered.groupby("customer_age", as_index=False)
            .agg(chiffre_affaires=("total_amount", "sum"))
            .sort_values("customer_age")
        )

        fig = px.line(
            age_data,
            x="customer_age",
            y="chiffre_affaires",
            markers=True,
            labels={
                "customer_age": "Âge du client",
                "chiffre_affaires": "CA (TND)",
            },
            title="CA selon l'âge du client",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.scatter(
            filtered,
            x="quantity",
            y="total_amount",
            size="rating",
            hover_data=["category", "region", "channel"],
            labels={
                "quantity": "Quantité",
                "total_amount": "Montant total (TND)",
            },
            title="Quantité vs montant de la commande",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Statistiques de paiement")
    st.dataframe(
        payment_stats.style.format(
            {
                "note_moyenne": "{:.2f}",
                "chiffre_affaires": "{:,.2f} TND",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# TAB 4 — REGIONAL ANALYSIS
# ============================================================

with tab_regions:
    st.markdown(
        '<div class="section-title">Analyse géographique des ventes</div>',
        unsafe_allow_html=True,
    )

    regional = (
        filtered.groupby("region", as_index=False)
        .agg(
            nb_commandes=("order_id", "nunique"),
            chiffre_affaires=("total_amount", "sum"),
            panier_moyen=("total_amount", "mean"),
            note_moyenne=("rating", "mean"),
        )
        .sort_values("chiffre_affaires", ascending=False)
    )

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            regional,
            x="region",
            y="chiffre_affaires",
            text_auto=".2s",
            labels={
                "region": "Région",
                "chiffre_affaires": "CA (TND)",
            },
            title="Chiffre d'affaires par région",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            regional,
            x="nb_commandes",
            y="chiffre_affaires",
            size="panier_moyen",
            hover_name="region",
            labels={
                "nb_commandes": "Nombre de commandes",
                "chiffre_affaires": "CA (TND)",
                "panier_moyen": "Panier moyen",
            },
            title="Commandes vs chiffre d'affaires",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Performance régionale")
    st.dataframe(
        regional.style.format(
            {
                "chiffre_affaires": "{:,.2f} TND",
                "panier_moyen": "{:,.2f} TND",
                "note_moyenne": "{:.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# TAB 5 — BIG DATA / SPARK
# ============================================================

with tab_bigdata:
    st.markdown(
        '<div class="section-title">Architecture Big Data du projet</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Cette partie reprend les concepts présentés dans votre notebook : "
        "HDFS simulé, partitionnement, réplication et traitement PySpark."
    )

    # Exact values from the project
    workers = 4
    replication_factor = 3
    dataset_rows = len(df)
    dataset_columns = len(df.columns)

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("📦 Enregistrements", f"{dataset_rows:,}".replace(",", " "))
    b2.metric("🧱 Partitions Spark", workers)
    b3.metric("🔁 Facteur de réplication", replication_factor)
    b4.metric("📐 Attributs", dataset_columns)

    st.markdown("### Pipeline du projet")

    st.code(
        """retail_sales_2024.csv
        ↓
HDFS simulé
(blocs / partitions + réplication)
        ↓
Apache Spark / PySpark
(local[4] → 4 workers simulés)
        ↓
groupBy / agg / filter
        ↓
Résultats analytiques
        ↓
Dashboard Streamlit""",
        language="text",
    )

    st.markdown("### Répartition simulée des données")

    # Deterministic 4-partition representation of the 8,000-row dataset.
    partition_ids = np.arange(len(df)) % workers
    partition_table = (
        pd.DataFrame({"partition": partition_ids})
        .value_counts()
        .sort_index()
        .rename("enregistrements")
        .reset_index()
    )
    partition_table["worker"] = (
        partition_table["partition"] + 1
    ).map(lambda x: f"Worker {x}")

    fig = px.bar(
        partition_table,
        x="worker",
        y="enregistrements",
        text_auto=True,
        labels={
            "worker": "Worker simulé",
            "enregistrements": "Enregistrements",
        },
        title="Répartition des enregistrements sur 4 partitions",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Concepts couverts")

    concepts = pd.DataFrame(
        {
            "Concept": [
                "Master / Driver",
                "Workers",
                "Partitionnement",
                "Réplication",
                "Traitement distribué",
                "Sauvegarde des résultats",
            ],
            "Implémentation dans le projet": [
                "Driver PySpark local",
                "4 threads avec local[4]",
                "4 partitions Spark",
                "3 copies simulées",
                "groupBy / agg / filter",
                "CSV + Parquet",
            ],
        }
    )

    st.dataframe(
        concepts,
        use_container_width=True,
        hide_index=True,
    )

    st.warning(
        "Important : ce projet simule un cluster Big Data sur une seule machine. "
        "Les 4 workers et la réplication ne correspondent pas à 4 machines physiques "
        "ou à un vrai cluster HDFS."
    )

# ============================================================
# TAB 6 — RAW DATA
# ============================================================

with tab_data:
    st.markdown(
        '<div class="section-title">Exploration des données</div>',
        unsafe_allow_html=True,
    )

    st.write(
        f"Dataset original : **{len(df):,} lignes × {len(df.columns)} colonnes**."
        .replace(",", " ")
    )

    make_download(filtered, "retail_sales_2024_filtered.csv")

    display_columns = [
        "order_id",
        "date",
        "category",
        "region",
        "channel",
        "payment_method",
        "quantity",
        "unit_price",
        "customer_age",
        "rating",
        "total_amount",
    ]

    st.dataframe(
        filtered[display_columns].sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Valeurs manquantes")

    missing = (
        filtered.isna()
        .sum()
        .reset_index()
        .rename(columns={"index": "colonne", 0: "valeurs_manquantes"})
    )

    st.dataframe(
        missing,
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Projet — Systèmes Répartis pour le Big Data | "
    "Retail Sales 2024 | PySpark + HDFS simulé + Streamlit"
)
