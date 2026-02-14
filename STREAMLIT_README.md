# 🏦 Banking API - Interface Streamlit

Interface web métier pour tester et visualiser l'API Banking Transactions.


---

## 🔗 Lien avec le projet principal

Cette interface Streamlit est développée pour tester l'API Banking Transactions.

📦 **Repository de l'API** : [projet_python_2_mba](https://github.com/CamilleThauvin/projet_python_2_mba)

---

## 🚀 Installation et Démarrage

### Prérequis

1. **L'API principale doit être installée et lancée** :
   
   # Cloner et installer l'API
   git clone https://github.com/CamilleThauvin/projet_python_2_mba.git
   cd projet_python_2_mba
   pip install -e .
   
   # Télécharger le dataset depuis Kaggle
   # Voir instructions dans le README de l'API
   
   # Lancer l'API
   uvicorn banking_api.main:app --reload
   # API accessible sur http://localhost:8000
   ```

2. **Python 3.8+**

### Installation de l'interface Streamlit


# Cloner ce repository
git clone https://github.com/payebie/banking-api-streamlit.git
cd banking-api-streamlit

# Installer les dépendances
pip install -r requirements.txt


### Lancement


streamlit run streamlit_app.py


L'interface s'ouvre automatiquement sur **http://localhost:8501**

---

## 📊 Fonctionnalités

### 1. 📈 Vue d'ensemble
- **KPIs en temps réel** : Total transactions, taux de fraude, montant moyen
- **Graphiques de distribution** : Par type de transaction
- **Visualisation du taux de fraude** par catégorie

### 2. 💳 Transactions
- Liste paginée avec filtres
- Filtres par type, fraude, montant
- Export CSV des résultats

### 3. 📊 Statistiques
- Stats par type de transaction
- Stats quotidiennes (évolution temporelle)
- Distribution des montants (histogramme)

### 4. 🚨 Détection de Fraude
- **Prédiction en temps réel**
- Formulaire interactif
- Résultats avec probabilités et raisons
- Visualisation des règles de détection

### 5. 👥 Clients
- Recherche par ID client
- Top clients (par volume ou nombre)
- Profils détaillés avec stats

### 6. 🔍 Recherche Avancée
- Multicritères (type, fraude, montant)
- Export des résultats

### 7. 🧪 Test des Routes
- Interface de test manuel pour toutes les routes API
- Paramètres personnalisables
- Affichage JSON des réponses

---

## 🎯 Workflow d'utilisation

### Terminal 1 : API Backend

cd projet_python_2_mba
uvicorn banking_api.main:app --reload
```

### Terminal 2 : Interface Streamlit

cd banking-api-streamlit
streamlit run streamlit_app.py
```

### Accès
- **API** : http://localhost:8000
- **Swagger** : http://localhost:8000/docs
- **Streamlit** : http://localhost:8501

---

## 🛠️ Technologies Utilisées

- **Streamlit** 1.40.2 - Framework web
- **Plotly** 5.24.1 - Graphiques interactifs
- **Pandas** 2.3.3 - Manipulation de données
- **Requests** 2.32.3 - Appels API