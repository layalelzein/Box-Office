import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Dashboard Box-Office", layout="wide", page_icon="🎬")

# Titre principal
st.title("🎬 Dashboard de rentabilité des films")

# Description de l'application
st.write("""
Bienvenue sur le **tableau de bord interactif Box-Office** ! 🎥  

Naviguez dans les différentes sections pour explorer :
- 📄 **Données brutes** : Analysez les films collectés.
- 📊 **ROI par genre** : Comparez la rentabilité par genre.
- 🏢 **Comparaison des studios** : Découvrez les performances des studios.
- 🤖 **Prédiction ROI** : Prédisez la rentabilité des films en fonction des caractéristiques.

Utilisez le menu à gauche pour accéder aux différentes pages. Profitez de votre exploration ! 🚀
""")

# Footer design
st.markdown("""
    <style>
    footer {visibility: hidden;}
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f5f7fa;
        text-align: center;
        padding: 10px;
        color: black;
    }
    </style>
    <div class="footer">
        <p>Développé par Layal Elzein & Léa Nassar</p>
    </div>
    """, unsafe_allow_html=True)
