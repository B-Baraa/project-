# 📊 Projet Big Data — Analyse Distribuée de Ventes Retail

> Projet réalisé dans le cadre du cours **Systèmes Répartis pour le Big Data**
> Simulation d'un cluster Hadoop/Spark (Master/Worker, HDFS, partitionnement, réplication) appliquée à un jeu de données réel de ventes retail.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PySpark](https://img.shields.io/badge/PySpark-3.x-orange?logo=apachespark)
![Status](https://img.shields.io/badge/status-completed-brightgreen)
![License](https://img.shields.io/badge/license-Academic-lightgrey)

---

## 🎯 Objectif du projet

Appliquer, sur un jeu de données concret, les notions du cours consacrées aux systèmes distribués et aux architectures Big Data :

- Architecture d'un cluster Big Data (Master Node / Worker Nodes)
- Stockage distribué (HDFS) : découpage en blocs, partitionnement, réplication, cohérence
- Traitement distribué avec Apache Spark / PySpark (principe MapReduce)
- Tolérance aux pannes et scalabilité horizontale
- Sauvegarde et visualisation des résultats

Le pipeline reproduit le schéma présenté en cours :

```
Dataset CSV  →  HDFS (stockage distribué)  →  Spark / PySpark (traitement)  →  Résultats (HDFS)
```

---

## 🗂️ Le dataset

**Fichier :** `retail_sales_2024.csv`
**Taille :** 8 000 enregistrements · 11 attributs
**Description :** ventes d'une enseigne retail en Tunisie sur l'année 2024.

| Colonne          | Description                          |
|------------------|---------------------------------------|
| `order_id`       | Identifiant de la commande            |
| `date`           | Date de la commande                   |
| `category`       | Catégorie de produit                  |
| `region`         | Région du client                      |
| `channel`        | Canal de vente (en ligne / magasin)   |
| `payment_method` | Moyen de paiement                     |
| `quantity`       | Quantité achetée                      |
| `unit_price`     | Prix unitaire                         |
| `customer_age`   | Âge du client                         |
| `rating`         | Note de satisfaction (1 à 5)          |
| `total_amount`   | Montant total de la commande          |

**Pourquoi ce dataset ?** Structuré, volumineux et réaliste — il permet d'illustrer de vraies opérations d'agrégation distribuée (chiffre d'affaires par catégorie/région, évolution mensuelle) tout en restant assez léger pour être exécuté et vérifié en local.

---

## 🏗️ Architecture du projet

Faute d'un vrai cluster multi-machines, le comportement d'un cluster Hadoop/Spark est **simulé sur une seule machine** : le code et les concepts (partitionnement, parallélisme, réplication) restent identiques à un déploiement réel.

| Composant du cours | Équivalent dans ce projet |
|---|---|
| **Master Node** (NameNode, ResourceManager, Spark Driver) | Driver PySpark local |
| **Worker Nodes** (DataNode, NodeManager, Spark Worker) | 4 threads Spark (`local[4]`) |
| **HDFS** (blocs, réplication) | Dossier `hdfs_simulation/` : 4 partitions + 2 répliques |
| **Traitement distribué** (MapReduce / Spark) | `groupBy().agg()` exécutés en parallèle sur les partitions |
| **Résultats sur HDFS** | Dossier `resultats/` (CSV + Parquet) |

```
                     ┌────────────────────────────┐
                     │        MASTER NODE          │
                     │ NameNode • ResourceManager  │
                     │        Spark Driver         │
                     └──────────────┬───────────────┘
             ┌───────────┬──────────┴──────────┬───────────┐
             ▼           ▼                     ▼           ▼
        ┌─────────┐ ┌─────────┐          ┌─────────┐ ┌─────────┐
        │Worker 1 │ │Worker 2 │          │Worker 3 │ │Worker 4 │
        │DataNode │ │DataNode │          │DataNode │ │DataNode │
        │YARN NM  │ │YARN NM  │          │YARN NM  │ │YARN NM  │
        │Spark Wkr│ │Spark Wkr│          │Spark Wkr│ │Spark Wkr│
        └────┬────┘ └────┬────┘          └────┬────┘ └────┬────┘
             └───────────┴─────── HDFS ────────┴───────────┘
                  Données distribuées et répliquées (x3)
```

---

## 🔄 Pipeline — étapes détaillées

### 1️⃣ Collecte et ingestion
Chargement du CSV dans un DataFrame Spark avec inférence de schéma (`spark.read.csv`), vérification des dimensions et des valeurs manquantes.

### 2️⃣ Simulation du stockage distribué (HDFS)
- **Partitionnement** : `df.repartition(4)` — le DataFrame est réparti en 4 blocs traités en parallèle, simulant la répartition sur 4 DataNodes.
- **Réplication** : chaque bloc est dupliqué 3 fois (`hdfs_simulation/blocs_partition`, `replique_2`, `replique_3`) — facteur de réplication par défaut de HDFS, garantissant la tolérance aux pannes.

### 3️⃣ Traitement distribué avec PySpark
Cinq agrégations exécutées en parallèle sur les partitions (principe Map/Reduce) :
- Chiffre d'affaires & nombre de commandes par **catégorie**
- Chiffre d'affaires par **région**
- Répartition des **moyens de paiement** + note de satisfaction moyenne
- **Évolution mensuelle** du chiffre d'affaires (traitement batch)
- Croisement **région × canal** de vente

### 4️⃣ Visualisation
Génération de graphiques (Matplotlib) : CA par catégorie, CA par région, évolution mensuelle.

### 5️⃣ Sauvegarde des résultats
Écriture des résultats en **CSV** et **Parquet** dans `resultats/`, simulant le retour des résultats vers HDFS.

### 6️⃣ Tolérance aux pannes & scalabilité *(discussion)*
Lien avec les mécanismes vus en cours : détection de pannes par heartbeat/timeout, redondance et reprise automatique, scalabilité horizontale (ajout de workers plutôt que d'augmenter la puissance d'une seule machine), et notions de monitoring (métriques, journaux, alertes).

---

## 📈 Résultats clés

- **Électronique** génère le chiffre d'affaires le plus élevé, suivi par **Meubles**.
- **Tunis** et **Sfax** concentrent les ventes les plus fortes par région.
- La **carte bancaire** est le moyen de paiement dominant.
- Le chiffre d'affaires mensuel reste globalement stable, avec quelques variations saisonnières.

---

## 📁 Structure du dépôt

```
.
├── retail_sales_2024.csv          # Dataset (8 000 x 11)
├── projet_bigdata_retail.ipynb    # Notebook PySpark complet (exécuté)
├── rapport_projet.md              # Rapport détaillé du projet
├── projet_bigdata_retail.pptx     # Présentation (architecture, étapes, résultats)
├── resultats/                     # Résultats exportés (CSV + Parquet)
│   ├── ca_par_categorie_csv/
│   ├── ca_par_categorie_parquet/
│   ├── ca_par_region_csv/
│   ├── ca_mensuel_csv/
│   └── canal_region_csv/
├── hdfs_simulation/                # Simulation du stockage distribué (blocs + répliques)
└── README.md
```

---

## ⚙️ Installation & exécution

### Prérequis
- Python 3.10+
- Java 11+ (requis par Spark)

### Installation

```bash
pip install pyspark pandas matplotlib jupyter
```

### Lancer le notebook

```bash
jupyter notebook projet_bigdata_retail.ipynb
```

Le notebook est fourni **déjà exécuté** : tous les tableaux et graphiques sont visibles directement, sans avoir besoin de relancer les cellules (sauf si vous souhaitez modifier le code).

### Exécuter uniquement le traitement Spark (sans Jupyter)

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("ProjetBigData").master("local[4]").getOrCreate()
df = spark.read.csv("retail_sales_2024.csv", header=True, inferSchema=True)

df.groupBy("category").agg(
    F.count("order_id").alias("nb_commandes"),
    F.round(F.sum("total_amount"), 2).alias("chiffre_affaires")
).orderBy(F.desc("chiffre_affaires")).show()
```

---

## 🧠 Concepts du cours illustrés

| Concept | Application dans le projet |
|---|---|
| **Partitionnement (Sharding)** | 8 000 lignes réparties en 4 partitions traitées en parallèle |
| **Réplication** | Chaque bloc dupliqué 3 fois pour la tolérance aux pannes |
| **Cohérence** | Cohérence forte simulée entre les répliques |
| **MapReduce / Spark** | `groupBy().agg()` exécutés en parallèle puis combinés |
| **Scalabilité horizontale** | `local[4]` → cluster YARN réel, sans changer la logique |
| **Détection de pannes** | Analogie avec heartbeat/timeout (HDFS réel) |

---

## ⚠️ Limites du projet

- Un seul poste utilisé : pas de vrai réseau, pas de vraies pannes matérielles.
- Réplication simulée par copie de fichiers, sans reprise sur panne automatique.
- Latence réseau, cohérence distribuée réelle et monitoring temps réel non testés.

## 🚀 Pistes d'amélioration

- Déployer le pipeline sur un vrai cluster Hadoop/YARN ou sur le cloud (AWS EMR, Databricks).
- Ajouter une couche de monitoring (Grafana / Prometheus) pour visualiser l'état du cluster en temps réel.
- Étendre le dataset avec un flux de données en continu (Kafka + Spark Streaming).

---

## 📄 Licence

Projet académique — libre d'utilisation à des fins pédagogiques.

## ✍️ Auteur

Projet réalisé dans le cadre du cours *Systèmes Répartis pour le Big Data*.
