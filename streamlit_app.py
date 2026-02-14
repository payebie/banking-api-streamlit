"""
Application Streamlit - Banking Transactions API Tester
=========================================================

Interface métier pour tester et visualiser les données de l'API Banking Transactions.

Projet:banking api streamlit - ESG 2025
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import json

# Configuration de la page
st.set_page_config(
    page_title="Banking API Tester",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de base de l'API
API_BASE_URL = "http://localhost:8000/api"


# ==================== FONCTIONS UTILITAIRES ====================

def check_api_health() -> bool:
    """Vérifie que l'API est accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/system/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def format_number(num: float) -> str:
    """Formate un nombre avec séparateurs de milliers."""
    return f"{num:,.2f}"


def get_api_data(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Récupère des données depuis l'API."""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur API: {str(e)}")
        return None


def post_api_data(endpoint: str, data: Dict) -> Optional[Dict]:
    """Envoie des données en POST à l'API."""
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur API: {str(e)}")
        return None


# ==================== HEADER ====================

st.title("🏦 Banking Transactions API - Interface de Test")
st.markdown("---")

# Vérification de l'état de l'API
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if check_api_health():
        st.success("✅ API connectée et fonctionnelle")
    else:
        st.error("❌ API non accessible. Assurez-vous que l'API tourne sur http://localhost:8000")
        st.info("💡 Lancez l'API avec : `uvicorn banking_api.main:app --reload`")
        st.stop()

with col2:
    metadata = get_api_data("system/metadata")
    if metadata:
        st.info(f"📦 Version: {metadata.get('version', 'N/A')}")

with col3:
    st.info(f"🔗 Base URL: `{API_BASE_URL}`")

st.markdown("---")


# ==================== SIDEBAR ====================

st.sidebar.title("📋 Navigation")
menu = st.sidebar.radio(
    "Choisissez une section :",
    [
        "📊 Vue d'ensemble",
        "💳 Transactions",
        "📈 Statistiques",
        "🚨 Détection de Fraude",
        "👥 Clients",
        "🔍 Recherche Avancée",
        "🧪 Test des Routes"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Points testés")
st.sidebar.markdown("""
- ✅ GET /transactions
- ✅ GET /stats/overview
- ✅ GET /fraud/summary
- ✅ POST /fraud/predict
- ✅ GET /customers
- ✅ POST /transactions/search
""")


# ==================== VUE D'ENSEMBLE ====================

if menu == "📊 Vue d'ensemble":
    st.header("📊 Vue d'Ensemble du Système")
    
    # Récupérer les stats globales
    overview = get_api_data("stats/overview")
    fraud_summary = get_api_data("fraud/summary")
    
    if overview and fraud_summary:
        # KPIs principaux
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Transactions",
                f"{overview['total_transactions']:,}",
                help="Nombre total de transactions dans le dataset"
            )
        
        with col2:
            fraud_rate_pct = overview['fraud_rate'] * 100
            st.metric(
                "Taux de Fraude",
                f"{fraud_rate_pct:.3f}%",
                delta=f"{fraud_summary['total_frauds']:,} fraudes",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Montant Moyen",
                f"${format_number(overview['avg_amount'])}",
                help="Montant moyen par transaction"
            )
        
        with col4:
            st.metric(
                "Type Principal",
                overview['most_common_type'],
                help="Type de transaction le plus fréquent"
            )
        
        st.markdown("---")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribution des Montants")
            dist_data = get_api_data("stats/amount-distribution")
            if dist_data:
                fig = px.bar(
                    x=dist_data['bins'],
                    y=dist_data['counts'],
                    labels={'x': 'Plage de montant', 'y': 'Nombre de transactions'},
                    title="Répartition des transactions par montant"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Statistiques par Type")
            stats_by_type = get_api_data("stats/by-type")
            if stats_by_type:
                df_types = pd.DataFrame(stats_by_type)
                fig = px.pie(
                    df_types,
                    values='count',
                    names='type',
                    title="Répartition par type de transaction"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Fraude par type
        st.subheader("🚨 Taux de Fraude par Type")
        fraud_by_type = get_api_data("fraud/by-type")
        if fraud_by_type:
            df_fraud = pd.DataFrame(fraud_by_type)
            fig = px.bar(
                df_fraud,
                x='type',
                y='fraud_rate',
                color='fraud_rate',
                labels={'type': 'Type de transaction', 'fraud_rate': 'Taux de fraude (%)'},
                title="Taux de fraude par type de transaction",
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)


# ==================== TRANSACTIONS ====================

elif menu == "💳 Transactions":
    st.header("💳 Consultation des Transactions")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        page = st.number_input("Page", min_value=1, value=1)
    
    with col2:
        limit = st.selectbox("Transactions par page", [10, 25, 50, 100], index=0)
    
    with col3:
        # Récupérer les types disponibles
        types_data = get_api_data("transactions/types")
        if types_data:
            transaction_types = ["Tous"] + types_data.get('types', [])
            selected_type = st.selectbox("Type de transaction", transaction_types)
    
    # Filtres additionnels
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fraud_filter = st.selectbox("Fraude", ["Toutes", "Frauduleuses", "Non frauduleuses"])
    
    with col2:
        min_amount = st.number_input("Montant minimum", min_value=0.0, value=0.0)
    
    with col3:
        max_amount = st.number_input("Montant maximum", min_value=0.0, value=0.0)
    
    # Construire les paramètres
    params = {
        "page": page,
        "limit": limit
    }
    
    if selected_type != "Tous":
        params["type"] = selected_type
    
    if fraud_filter == "Frauduleuses":
        params["isFraud"] = 1
    elif fraud_filter == "Non frauduleuses":
        params["isFraud"] = 0
    
    if min_amount > 0:
        params["min_amount"] = min_amount
    
    if max_amount > 0:
        params["max_amount"] = max_amount
    
    # Bouton de recherche
    if st.button("🔍 Rechercher", type="primary"):
        data = get_api_data("transactions", params=params)
        
        if data:
            st.success(f"✅ {data['total']} transactions trouvées")
            
            if data['transactions']:
                df = pd.DataFrame(data['transactions'])
                
                # Formater l'affichage
                st.dataframe(
                    df,
                    use_container_width=True,
                    height=400
                )
                
                # Téléchargement CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger en CSV",
                    data=csv,
                    file_name="transactions.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Aucune transaction trouvée avec ces critères")
    
    # Section Transactions récentes
    st.markdown("---")
    st.subheader("🕐 Transactions Récentes")
    
    n_recent = st.slider("Nombre de transactions", min_value=5, max_value=50, value=10)
    
    if st.button("Afficher les transactions récentes"):
        recent_data = get_api_data("transactions/recent", params={"n": n_recent})
        
        if recent_data and recent_data.get('transactions'):
            df_recent = pd.DataFrame(recent_data['transactions'])
            st.dataframe(df_recent, use_container_width=True)


# ==================== STATISTIQUES ====================

elif menu == "📈 Statistiques":
    st.header("📈 Statistiques Détaillées")
    
    tab1, tab2, tab3 = st.tabs(["📊 Par Type", "📅 Quotidiennes", "💰 Distribution"])
    
    with tab1:
        st.subheader("Statistiques par Type de Transaction")
        stats_by_type = get_api_data("stats/by-type")
        
        if stats_by_type:
            df_stats = pd.DataFrame(stats_by_type)
            
            # Tableau
            st.dataframe(
                df_stats.style.format({
                    'count': '{:,}',
                    'avg_amount': '${:,.2f}',
                    'total_amount': '${:,.2f}'
                }),
                use_container_width=True
            )
            
            # Graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    df_stats,
                    x='type',
                    y='count',
                    title="Nombre de transactions par type",
                    labels={'count': 'Nombre', 'type': 'Type'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    df_stats,
                    x='type',
                    y='avg_amount',
                    title="Montant moyen par type",
                    labels={'avg_amount': 'Montant moyen ($)', 'type': 'Type'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Statistiques Quotidiennes (par step)")
        daily_stats = get_api_data("stats/daily")
        
        if daily_stats:
            df_daily = pd.DataFrame(daily_stats)
            
            # Graphique d'évolution
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_daily['day'],
                y=df_daily['count'],
                mode='lines+markers',
                name='Nombre de transactions',
                yaxis='y1'
            ))
            fig.add_trace(go.Scatter(
                x=df_daily['day'],
                y=df_daily['avg_amount'],
                mode='lines+markers',
                name='Montant moyen',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="Évolution quotidienne des transactions",
                xaxis_title="Jour (step)",
                yaxis=dict(title="Nombre de transactions"),
                yaxis2=dict(title="Montant moyen ($)", overlaying='y', side='right')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau détaillé
            st.dataframe(
                df_daily.style.format({
                    'count': '{:,}',
                    'avg_amount': '${:,.2f}',
                    'total_amount': '${:,.2f}'
                }),
                use_container_width=True
            )
    
    with tab3:
        st.subheader("Distribution des Montants")
        dist_data = get_api_data("stats/amount-distribution")
        
        if dist_data:
            df_dist = pd.DataFrame({
                'Plage': dist_data['bins'],
                'Nombre': dist_data['counts']
            })
            
            fig = px.bar(
                df_dist,
                x='Plage',
                y='Nombre',
                title="Distribution des montants de transactions"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_dist, use_container_width=True)


# ==================== DÉTECTION DE FRAUDE ====================

elif menu == "🚨 Détection de Fraude":
    st.header("🚨 Détection et Analyse de Fraude")
    
    # Résumé de fraude
    fraud_summary = get_api_data("fraud/summary")
    
    if fraud_summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Fraudes", f"{fraud_summary['total_frauds']:,}")
        
        with col2:
            st.metric("Fraudes Détectées", f"{fraud_summary['flagged']:,}")
        
        with col3:
            st.metric("Précision", f"{fraud_summary['precision']:.2%}")
        
        with col4:
            st.metric("Rappel", f"{fraud_summary['recall']:.2%}")
    
    st.markdown("---")
    
    # Prédiction de fraude
    st.subheader("🎯 Prédiction de Fraude")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Informations de la transaction**")
        
        transaction_type = st.selectbox(
            "Type de transaction",
            ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]
        )
        
        amount = st.number_input(
            "Montant",
            min_value=0.0,
            value=1000.0,
            step=100.0
        )
        
        oldbalance_org = st.number_input(
            "Solde avant (émetteur)",
            min_value=0.0,
            value=5000.0,
            step=100.0
        )
        
        newbalance_orig = st.number_input(
            "Solde après (émetteur)",
            min_value=0.0,
            value=4000.0,
            step=100.0
        )
    
    with col2:
        st.markdown("**Résultat de la prédiction**")
        
        if st.button("🔍 Analyser la transaction", type="primary"):
            prediction_data = {
                "type": transaction_type,
                "amount": amount,
                "oldbalanceOrg": oldbalance_org,
                "newbalanceOrig": newbalance_orig
            }
            
            result = post_api_data("fraud/predict", prediction_data)
            
            if result:
                if result['isFraud']:
                    st.error("⚠️ TRANSACTION SUSPECTE !")
                    st.metric("Probabilité de fraude", f"{result['probability']:.1%}")
                else:
                    st.success("✅ Transaction normale")
                    st.metric("Probabilité de fraude", f"{result['probability']:.1%}")
                
                st.markdown("**Raisons détectées :**")
                for reason in result['reasons']:
                    st.write(f"• {reason}")
                
                # JSON brut
                with st.expander("📄 Voir la réponse JSON"):
                    st.json(result)
    
    st.markdown("---")
    
    # Fraude par type
    st.subheader("📊 Analyse de Fraude par Type")
    fraud_by_type = get_api_data("fraud/by-type")
    
    if fraud_by_type:
        df_fraud = pd.DataFrame(fraud_by_type)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(
                df_fraud.style.format({
                    'total_transactions': '{:,}',
                    'fraud_count': '{:,}',
                    'fraud_rate': '{:.2f}%'
                }),
                use_container_width=True
            )
        
        with col2:
            fig = px.bar(
                df_fraud,
                x='type',
                y='fraud_count',
                color='fraud_rate',
                title="Nombre de fraudes par type",
                labels={'fraud_count': 'Nombre de fraudes', 'type': 'Type'},
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)


# ==================== CLIENTS ====================

elif menu == "👥 Clients":
    st.header("👥 Gestion des Clients")
    
    tab1, tab2, tab3 = st.tabs(["📋 Liste", "🏆 Top Clients", "👤 Profil"])
    
    with tab1:
        st.subheader("Liste des Clients")
        
        col1, col2 = st.columns(2)
        
        with col1:
            page = st.number_input("Page", min_value=1, value=1, key="customers_page")
        
        with col2:
            limit = st.selectbox("Clients par page", [10, 25, 50], key="customers_limit")
        
        if st.button("📋 Afficher les clients"):
            customers_data = get_api_data("customers", params={"page": page, "limit": limit})
            
            if customers_data:
                st.info(f"Total de clients : {customers_data['total']:,}")
                
                df_customers = pd.DataFrame({
                    'ID Client': customers_data['customers']
                })
                st.dataframe(df_customers, use_container_width=True)
    
    with tab2:
        st.subheader("🏆 Top Clients")
        
        col1, col2 = st.columns(2)
        
        with col1:
            n_top = st.slider("Nombre de clients", min_value=5, max_value=50, value=10)
        
        with col2:
            sort_by = st.selectbox("Trier par", ["volume", "count"])
        
        if st.button("🏆 Afficher le top"):
            top_customers = get_api_data("customers/top", params={"n": n_top, "by": sort_by})
            
            if top_customers:
                df_top = pd.DataFrame(top_customers)
                
                st.dataframe(
                    df_top.style.format({
                        'transaction_count': '{:,}',
                        'total_amount': '${:,.2f}',
                        'avg_amount': '${:,.2f}',
                        'fraud_count': '{:,}'
                    }),
                    use_container_width=True
                )
                
                # Graphique
                fig = px.bar(
                    df_top,
                    x='customer_id',
                    y='total_amount' if sort_by == 'volume' else 'transaction_count',
                    color='fraudulent',
                    title=f"Top {n_top} clients par {'volume' if sort_by == 'volume' else 'nombre de transactions'}",
                    labels={
                        'total_amount': 'Volume total ($)',
                        'transaction_count': 'Nombre de transactions',
                        'customer_id': 'Client'
                    },
                    color_discrete_map={True: 'red', False: 'green'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("👤 Profil Client Détaillé")
        
        customer_id = st.text_input("ID du client", placeholder="Ex: C1231006815")
        
        if st.button("🔍 Rechercher le profil"):
            if customer_id:
                profile = get_api_data(f"customers/{customer_id}")
                
                if profile:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Transactions", f"{profile['transactions_count']:,}")
                    
                    with col2:
                        st.metric("Montant Total", f"${format_number(profile['total_amount'])}")
                    
                    with col3:
                        st.metric("Montant Moyen", f"${format_number(profile['avg_amount'])}")
                    
                    with col4:
                        fraud_status = "⚠️ Frauduleux" if profile['fraudulent'] else "✅ Normal"
                        st.metric("Statut", fraud_status)
                    
                    if profile['fraudulent']:
                        st.error(f"🚨 Ce client a {profile['fraud_count']} transaction(s) frauduleuse(s)")
                    
                    # Transactions du client
                    st.markdown("---")
                    st.subheader("Transactions du client")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📤 Transactions émises"):
                            trans_data = get_api_data(f"transactions/by-customer/{customer_id}")
                            if trans_data:
                                df_trans = pd.DataFrame(trans_data['transactions'])
                                st.dataframe(df_trans, use_container_width=True)
                    
                    with col2:
                        if st.button("📥 Transactions reçues"):
                            trans_data = get_api_data(f"transactions/to-customer/{customer_id}")
                            if trans_data:
                                df_trans = pd.DataFrame(trans_data['transactions'])
                                st.dataframe(df_trans, use_container_width=True)
            else:
                st.warning("Veuillez entrer un ID client")


# ==================== RECHERCHE AVANCÉE ====================

elif menu == "🔍 Recherche Avancée":
    st.header("🔍 Recherche Multicritère")
    
    st.markdown("**Critères de recherche**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        types_data = get_api_data("transactions/types")
        if types_data:
            transaction_types = ["Tous"] + types_data.get('types', [])
            search_type = st.selectbox("Type", transaction_types, key="search_type")
    
    with col2:
        fraud_search = st.selectbox("Fraude", ["Toutes", "Oui", "Non"], key="search_fraud")
    
    with col3:
        st.write("")  # Spacer
    
    col1, col2 = st.columns(2)
    
    with col1:
        amount_min_search = st.number_input("Montant minimum", min_value=0.0, value=0.0, key="search_min")
    
    with col2:
        amount_max_search = st.number_input("Montant maximum", min_value=0.0, value=0.0, key="search_max")
    
    if st.button("🔎 Lancer la recherche", type="primary"):
        search_data = {}
        
        if search_type != "Tous":
            search_data["type"] = search_type
        
        if fraud_search == "Oui":
            search_data["isFraud"] = 1
        elif fraud_search == "Non":
            search_data["isFraud"] = 0
        
        if amount_min_search > 0 or amount_max_search > 0:
            search_data["amount_range"] = [
                amount_min_search if amount_min_search > 0 else 0,
                amount_max_search if amount_max_search > 0 else 999999999
            ]
        
        result = post_api_data("transactions/search", search_data)
        
        if result:
            st.success(f"✅ {result['count']} transactions trouvées")
            
            if result['transactions']:
                df_search = pd.DataFrame(result['transactions'])
                
                st.dataframe(df_search, use_container_width=True, height=400)
                
                # Statistiques rapides
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Nombre", len(df_search))
                
                with col2:
                    st.metric("Montant Total", f"${format_number(df_search['amount'].sum())}")
                
                with col3:
                    st.metric("Montant Moyen", f"${format_number(df_search['amount'].mean())}")
                
                # Téléchargement
                csv = df_search.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les résultats (CSV)",
                    data=csv,
                    file_name="search_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("Aucun résultat trouvé")


# ==================== TEST DES ROUTES ====================

elif menu == "🧪 Test des Routes":
    st.header("🧪 Test Manuel des Routes API")
    
    st.markdown("""
    Cette section permet de tester directement toutes les routes de l'API avec des requêtes personnalisées.
    """)
    
    # Sélection de la route
    route_category = st.selectbox(
        "Catégorie",
        ["Transactions", "Statistiques", "Fraude", "Clients", "Système"]
    )
    
    if route_category == "Transactions":
        routes = {
            "GET /transactions": {"method": "GET", "endpoint": "transactions"},
            "GET /transactions/{id}": {"method": "GET", "endpoint": "transactions/0"},
            "GET /transactions/types": {"method": "GET", "endpoint": "transactions/types"},
            "GET /transactions/recent": {"method": "GET", "endpoint": "transactions/recent"},
            "POST /transactions/search": {"method": "POST", "endpoint": "transactions/search"},
        }
    
    elif route_category == "Statistiques":
        routes = {
            "GET /stats/overview": {"method": "GET", "endpoint": "stats/overview"},
            "GET /stats/amount-distribution": {"method": "GET", "endpoint": "stats/amount-distribution"},
            "GET /stats/by-type": {"method": "GET", "endpoint": "stats/by-type"},
            "GET /stats/daily": {"method": "GET", "endpoint": "stats/daily"},
        }
    
    elif route_category == "Fraude":
        routes = {
            "GET /fraud/summary": {"method": "GET", "endpoint": "fraud/summary"},
            "GET /fraud/by-type": {"method": "GET", "endpoint": "fraud/by-type"},
            "POST /fraud/predict": {"method": "POST", "endpoint": "fraud/predict"},
        }
    
    elif route_category == "Clients":
        routes = {
            "GET /customers": {"method": "GET", "endpoint": "customers"},
            "GET /customers/{id}": {"method": "GET", "endpoint": "customers/C1231006815"},
            "GET /customers/top": {"method": "GET", "endpoint": "customers/top"},
        }
    
    else:  # Système
        routes = {
            "GET /system/health": {"method": "GET", "endpoint": "system/health"},
            "GET /system/metadata": {"method": "GET", "endpoint": "system/metadata"},
        }
    
    selected_route = st.selectbox("Route", list(routes.keys()))
    route_info = routes[selected_route]
    
    # Paramètres
    st.markdown("**Paramètres**")
    
    if route_info["method"] == "GET":
        params_text = st.text_area(
            "Query parameters (JSON)",
            value='{}',
            height=100,
            help="Ex: {\"page\": 1, \"limit\": 10}"
        )
    else:
        params_text = st.text_area(
            "Request body (JSON)",
            value='{}',
            height=150,
            help="Ex: {\"type\": \"TRANSFER\", \"amount\": 5000}"
        )
    
    # Bouton de test
    if st.button("🚀 Tester la route", type="primary"):
        try:
            params = json.loads(params_text)
            
            if route_info["method"] == "GET":
                result = get_api_data(route_info["endpoint"], params=params)
            else:
                result = post_api_data(route_info["endpoint"], params)
            
            if result:
                st.success("✅ Requête réussie")
                
                # Affichage JSON
                st.json(result)
                
                # Copie facile
                st.code(json.dumps(result, indent=2), language="json")
        
        except json.JSONDecodeError:
            st.error("❌ JSON invalide")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")


# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🏦 Banking Transactions API Tester v1.0.0</p>
    <p>📚 <a href='http://localhost:8000/docs' target='_blank'>Documentation Swagger</a> | 
       📊 <a href='http://localhost:8000/redoc' target='_blank'>ReDoc</a></p>
</div>
""", unsafe_allow_html=True)
