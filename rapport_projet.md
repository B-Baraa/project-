# Rapport de projet — Systèmes Répartis pour le Big Data
### Analyse distribuée d'un jeu de ventes retail avec Hadoop/HDFS (simulé) et PySpark

## 1. Contexte et objectif

Ce projet applique les concepts vus dans le cours *Systèmes Répartis pour le Big Data* (systèmes distribués, architecture Big Data, clusters Hadoop, HDFS, partitionnement, réplication, cohérence) sur un jeu de données concret, en suivant le schéma présenté en cours :

```
Dataset CSV  →  HDFS (stockage distribué)  →  Spark / PySpark (traitement)  →  Résultats (HDFS)
```

## 2. Le jeu de données

**Nom :** `retail_sales_2024.csv`
**Taille :** 8 000 enregistrements, 11 attributs
**Description :** ventes d'une enseigne retail en Tunisie sur l'année 2024.

| Colonne | Description |
|---|---|
| order_id | Identifiant unique de la commande |
| date | Date de la commande |
| category | Catégorie de produit (Électronique, Vêtements, Alimentation, …) |
| region | Région du client (Tunis, Sfax, Sousse, …) |
| channel | Canal de vente (En ligne / Magasin) |
| payment_method | Moyen de paiement |
| quantity | Quantité achetée |
| unit_price | Prix unitaire |
| customer_age | Âge du client |
| rating | Note de satisfaction (1 à 5) |
| total_amount | Montant total de la commande |

Ce type de données (structuré, tabulaire, volumineux) correspond exactement au type de données pris en charge par une architecture Big Data (cf. diapositive *« Qu'est-ce qu'une architecture Big Data »*).

## 3. Architecture retenue

| Composant théorique (cours) | Équivalent utilisé dans le projet |
|---|---|
| Master Node (NameNode, ResourceManager, Spark Driver) | Driver PySpark local |
| Worker Nodes (DataNode, NodeManager, Spark Worker) | 4 threads Spark (`local[4]`) simulant 4 nœuds de calcul |
| HDFS (blocs, réplication) | Dossier `hdfs_simulation/` avec 4 partitions + 2 répliques |
| Traitement distribué (MapReduce/Spark) | Transformations et agrégations PySpark (`groupBy`, `agg`) |

Faute d'un vrai cluster multi-machines, le comportement d'un cluster Hadoop/Spark est **simulé sur une seule machine** : le code, les concepts (partitionnement, parallélisme, réplication, cohérence) et le flux de données restent identiques à ceux d'un déploiement réel sur un cluster physique.

## 4. Étapes réalisées (voir le notebook `projet_bigdata_retail.ipynb`)

1. **Collecte et ingestion** : chargement du CSV dans un DataFrame Spark.
2. **Simulation du stockage distribué (HDFS)** :
   - Repartitionnement du DataFrame en 4 partitions (simulant le découpage en blocs répartis sur 4 DataNodes).
   - Écriture de 3 copies des blocs sur disque (facteur de réplication = 3, comme HDFS par défaut) pour illustrer la tolérance aux pannes.
3. **Traitement distribué avec PySpark** :
   - Chiffre d'affaires et nombre de commandes par catégorie de produit.
   - Chiffre d'affaires par région.
   - Répartition des moyens de paiement et note moyenne de satisfaction.
   - Évolution mensuelle du chiffre d'affaires (traitement batch sur données historiques).
   - Croisement région × canal de vente.
4. **Visualisation** des résultats (3 graphiques).
5. **Sauvegarde des résultats** dans un dossier `resultats/`, aux formats CSV et Parquet — simulant le retour des résultats vers HDFS.

## 5. Résultats principaux

- La catégorie **Électronique** génère le chiffre d'affaires le plus élevé, suivie par **Meubles**.
- Le canal **En ligne** représente une part importante des ventes selon les régions (voir le croisement région × canal dans le notebook).
- La **carte bancaire** est le moyen de paiement le plus utilisé.
- Le chiffre d'affaires mensuel montre une évolution assez stable sur l'année, avec quelques variations saisonnières.

(Le détail chiffré et les graphiques figurent dans le notebook joint.)

## 6. Lien avec les concepts du cours

- **Partitionnement (Sharding)** : les 8 000 lignes ont été réparties en 4 partitions traitées en parallèle, comme les blocs HDFS répartis sur plusieurs nœuds (cf. diapositive *« Partitionnement, réplication et cohérence »*).
- **Réplication** : chaque bloc a été dupliqué 3 fois, reproduisant le facteur de réplication par défaut de HDFS ; en cas de panne d'un nœud, les copies restantes garantissent la disponibilité des données.
- **Cohérence** : une cohérence forte a été simulée (toutes les répliques sont identiques dès l'écriture) ; sur un vrai cluster HDFS, ce résultat est obtenu via un mécanisme de heartbeat entre le NameNode et les DataNodes.
- **Traitement distribué (type MapReduce)** : chaque agrégation Spark (`groupBy().agg()`) est exécutée en parallèle sur les 4 partitions, puis les résultats partiels sont combinés (« reduce ») — exactement le principe illustré dans le cours (diapositive *« Principe de fonctionnement d'un cluster Big Data »*).

## 7. Avantages et limites observés

**Avantages :**
- Traitement rapide, même en environnement simulé, grâce au parallélisme.
- Résilience : la disponibilité des données ne dépend pas d'un seul nœud.
- Scalabilité horizontale : il suffirait de remplacer `local[4]` par une vraie configuration de cluster (YARN, Kubernetes) pour traiter un volume beaucoup plus important, sans changer la logique de traitement.

**Limites du projet :**
- Un seul poste est utilisé : pas de vrai réseau, pas de vraies pannes de nœuds à gérer.
- La réplication est simulée par une simple copie de fichiers, sans reprise sur panne automatique comme le ferait réellement HDFS.

## 8. Conclusion

Ce projet a permis de mettre en pratique, sur un jeu de données réaliste, les notions théoriques du cours : architecture Master/Worker, stockage distribué avec partitionnement et réplication (HDFS), traitement distribué (Spark/PySpark), et sauvegarde des résultats — reproduisant fidèlement le pipeline Big Data présenté en cours.

**Livrables :**
- `retail_sales_2024.csv` — le jeu de données utilisé
- `projet_bigdata_retail.ipynb` — le notebook PySpark complet (exécuté, avec résultats et graphiques)
- `rapport_projet.md` — ce rapport
