import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(
    page_title="MyBudget",
    page_icon="💰",
    layout="centered"
)

# ==================== Couleurs et style ====================
st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #2E7D32, #1B5E20);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }
        .budget-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 10px 0;
        }
        .total-card {
            background: linear-gradient(135deg, #FF6B6B, #FF4757);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# En-tête personnalisé
st.markdown('<div class="main-header"><h1>💰 MyBudget</h1><p>Gère ton argent simplement</p></div>', unsafe_allow_html=True)

# ==================== Gestion des données ====================

FICHIER_DONNEES = "budget_data.json"

# Catégories simplifiées
CATEGORIES = [
    "🍔 Nourriture",
    "🏠 Logement", 
    "🚌 Transport",
    "🎓 Études",
    "🎮 Loisirs",
    "🏥 Santé",
    "📱 Téléphone",
    "🎁 Autres"
]

def charger_donnees():
    """Charge les dépenses"""
    if os.path.exists(FICHIER_DONNEES):
        with open(FICHIER_DONNEES, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauvegarder_donnees(donnees):
    """Sauvegarde les dépenses"""
    with open(FICHIER_DONNEES, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

# ==================== Ajouter une dépense ====================

st.subheader("➕ Nouvelle dépense")

col1, col2 = st.columns(2)

with col1:
    categorie = st.selectbox("Catégorie", CATEGORIES)

with col2:
    montant = st.number_input("Montant (€)", min_value=0.01, step=1.0, format="%.2f")

description = st.text_input("Description", placeholder="Ex: Café, Livre, Transport...")

if st.button("💾 Enregistrer la dépense", use_container_width=True):
    if montant > 0 and description:
        donnees = charger_donnees()
        donnees.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "categorie": categorie,
            "montant": montant,
            "description": description
        })
        sauvegarder_donnees(donnees)
        st.success("✅ Dépense enregistrée !")
        st.rerun()
    else:
        st.error("❌ Remplis le montant et la description")

st.divider()

# ==================== Afficher les statistiques ====================

donnees = charger_donnees()

if donnees:
    df = pd.DataFrame(donnees)
    df["date"] = pd.to_datetime(df["date"])
    
    # ==================== Cartes ====================
    total = df["montant"].sum()
    nb_depenses = len(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="total-card">', unsafe_allow_html=True)
        st.metric("💰 Total dépensé", f"{total:.2f} €")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="budget-card">', unsafe_allow_html=True)
        st.metric("📝 Nombre de dépenses", nb_depenses)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        moyenne = total / nb_depenses if nb_depenses > 0 else 0
        st.markdown('<div class="budget-card">', unsafe_allow_html=True)
        st.metric("📊 Moyenne par dépense", f"{moyenne:.2f} €")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # ==================== Graphique simple ====================
    st.subheader("📊 Répartition des dépenses")
    
    somme_par_categorie = df.groupby("categorie")["montant"].sum().reset_index()
    
    # Graphique circulaire simple
    fig = px.pie(
        somme_par_categorie,
        values="montant",
        names="categorie",
        title="Où va ton argent ?",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== Liste des dépenses ====================
    st.subheader("📋 Liste des dépenses")
    
    # Filtrer par catégorie
    toutes_categories = ["Toutes"] + CATEGORIES
    filtre = st.selectbox("Filtrer par catégorie", toutes_categories)
    
    if filtre != "Toutes":
        df_filtre = df[df["categorie"] == filtre]
    else:
        df_filtre = df
    
    # Afficher le tableau
    tableau = df_filtre[["date", "categorie", "montant", "description"]].copy()
    tableau["date"] = tableau["date"].dt.strftime("%d/%m/%Y")
    tableau.columns = ["Date", "Catégorie", "Montant (€)", "Description"]
    
    st.dataframe(tableau, use_container_width=True, hide_index=True)
    
    # ==================== Supprimer une dépense ====================
    with st.expander("🗑️ Supprimer une dépense"):
        if len(donnees) > 0:
            options = [f"{t['date']} | {t['categorie']} | {t['montant']}€ | {t['description']}" for t in donnees]
            index = st.selectbox("Choisis la dépense à supprimer", range(len(options)), format_func=lambda x: options[x])
            if st.button("🗑️ Supprimer", use_container_width=True):
                donnees.pop(index)
                sauvegarder_donnees(donnees)
                st.success("Dépense supprimée !")
                st.rerun()
        else:
            st.info("Aucune dépense à supprimer")

else:
    st.info("💡 Aucune dépense pour le moment. Ajoute ta première dépense ci-dessus !")

# ==================== Conseils financiers ====================
st.divider()
with st.expander("💡 Conseils financiers pour étudiants"):
    st.markdown("""
    - **🎯 Fixe un budget mensuel** : Ne le dépasse pas et respecte les limites que tu t'es fixées.
    - **📱 Utilise l'application quotidiennement** : Note tes dépenses immédiatement pour savoir où va ton argent.
    - **🍽️ Cuisine à la maison** : C'est beaucoup moins cher que de manger au restaurant.
    - **🎓 Profite des réductions étudiantes** : Transports, restaurants, activités culturelles.
    - **💰 Épargne même un petit montant** : 20€ par mois peuvent devenir une somme importante.
    - **🚫 Évite les achats impulsifs** : Attends 24 heures avant d'acheter quelque chose dont tu n'as pas vraiment besoin.
    """)