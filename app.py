import streamlit as st
import pronotepy
from pronotepy.ent import *

# Configuration initiale
st.set_page_config(page_title="Contrôle Continu", page_icon="📚")

# Barème des points par niveau de maîtrise
bareme_points = {
    "Très bonne maîtrise": 50,
    "Maîtrise satisfaisante": 40,
    "Maîtrise fragile": 25,
    "Maîtrise insuffisante": 10
}

# Fonctions
def niveaux_maitrise_inverses():
    return {v: k for k, v in bareme_points.items()}

def moyenne_a_maitrise(moyenne):
    niveaux_inverses = niveaux_maitrise_inverses()
    niveaux = sorted(niveaux_inverses.keys())
    for i in range(len(niveaux) - 1):
        if moyenne >= niveaux[i] and moyenne < niveaux[i + 1]:
            return niveaux_inverses[niveaux[i + 1]]
    return niveaux_inverses[niveaux[-1]]

# Fonction pour arrondir au niveau de maîtrise supérieur
def arrondir_maitrise(moyenne):
    niveaux_inverses = niveaux_maitrise_inverses()
    niveaux = sorted(niveaux_inverses.keys())

    if not niveaux:  # Vérifie si la liste des niveaux est vide
        return None

    # Si la moyenne est inférieure au premier seuil, retourner le niveau associé à ce seuil.
    if moyenne < niveaux[0]:
        return niveaux_inverses[niveaux[0]]

    for i in range(len(niveaux) - 1):
        if moyenne >= niveaux[i] and moyenne < niveaux[i + 1]:
            # Calculez la différence avec le seuil inférieur et supérieur
            diff_inferieur = moyenne - niveaux[i]
            diff_superieur = niveaux[i + 1] - moyenne
            
            # Choisissez le seuil le plus proche
            if diff_inferieur <= diff_superieur:
                return niveaux_inverses[niveaux[i]]
            else:
                return niveaux_inverses[niveaux[i + 1]]

# Gestion de session pour maintenir l'état
if 'client' not in st.session_state:
    st.session_state.client = None

def connecter():
    selected_cas = cas if college_selectionne == 'Autre' else colleges[college_selectionne][1]
    st.session_state.client = pronotepy.Client(url if college_selectionne == 'Autre' else colleges[college_selectionne][0], username, password, getattr(pronotepy.ent, selected_cas, None)) 
    if not st.session_state.client.logged_in:
        st.error("Erreur de connexion. Veuillez vérifier vos identifiants.")
    else:
        st.success("Connecté avec succès !")

def deconnecter():
    st.session_state.client = None
    st.rerun()

# Interface utilisateur
st.title('Contrôle Continu 📚')

# Définition des options du menu déroulant
colleges = {
    'Autre': ('', ''),
    'Louise Weiss': ('https://0952236p.index-education.net/pronote/eleve.html', 'val_doise'),
}

cas_options = [
    'Aucune', 'ac_orleans_tours', 'ac_poitiers', 'ac_reunion', 'ac_reims', 
    'ac_rennes', 'atrium_sud', 'cas_agora06', 'cas_arsene76_edu', 'cas_cybercolleges42_edu', 
    'cas_kosmos', 'cas_seinesaintdenis_edu', 'eclat_bfc', 'ecollege_haute_garonne_edu', 
    'ent_94', 'ent_auvergnerhonealpe', 'ent_creuse', 'ent_creuse_educonnect', 'ent_elyco', 
    'ent_essonne', 'ent_hdf', 'ent_mayotte', 'ent_somme', 'ent_var', 'ent77', 
    'ent_ecollege78', 'extranet_colleges_somme', 'ile_de_france', 'laclasse_educonnect', 
    'laclasse_lyon', 'l_normandie', 'lyceeconnecte_aquitaine', 'lyceeconnecte_edu', 
    'monbureaunumerique', 'neoconnect_guadeloupe', 'occitanie_montpellier', 
    'occitanie_montpellier_educonnect', 'occitanie_toulouse_edu', 'paris_classe_numerique', 
    'val_de_marne', 'val_doise'
]

if st.session_state.client is None:
    college_selectionne = st.selectbox("🏫 Choisissez votre collège :", list(colleges.keys()))
    cas = st.selectbox("📍 Si votre collège n'est pas listé, choisissez votre cas :", cas_options) if college_selectionne == 'Autre' else colleges[college_selectionne][1]
    url = st.text_input('🧷 URL Pronote', value=colleges[college_selectionne][0]) if college_selectionne == 'Autre' else colleges[college_selectionne][0]
    username = st.text_input('1️⃣ Nom d\'utilisateur', '')
    password = st.text_input('2️⃣ Mot de passe', '', type='password')

    st.button('🟢 Se connecter', on_click=connecter)
else:
        if st.button('🔴 Se déconnecter'):
            deconnecter()

        # Sélection de la période
        periode = st.selectbox("🏫 Voir mes points par domaines des autres Périodes :", ["Contrôle Continu (Toute l'année)", "Trimestre 1", "Trimestre 2", "Trimestre 3"], index=0)
        periode_selectionnee = 0 if periode == "Contrôle Continu (Toute l'année)" else int(periode.replace('Trimestre ', ''))

        # Initialisation des dictionnaires pour stocker les points par domaine
        total_points_par_domaine = {}
        nombre_acquisitions_par_domaine = {}
        total_arrondi = 0

        if periode_selectionnee in [1, 2, 3]:
            current_period = [st.session_state.client.periods[periode_selectionnee - 1]]
        else:
            current_period = st.session_state.client.periods

        for period in current_period:
            evaluations = period.evaluations
            for evaluation in evaluations:
                for acquisition in evaluation.acquisitions:
                    domaines = acquisition.pillar_prefix.split(", ")
                    niveau_maitrise = acquisition.level
                    coefficient = acquisition.coefficient  # Récupère le coefficient de l'acquisition
                    points = bareme_points.get(niveau_maitrise, 0) * coefficient  # Multiplie les points par le coefficient

                    for domaine in domaines:
                        if domaine != "":
                            if domaine not in total_points_par_domaine:
                                total_points_par_domaine[domaine] = points
                                nombre_acquisitions_par_domaine[domaine] = 1
                            else:
                                total_points_par_domaine[domaine] += points
                                nombre_acquisitions_par_domaine[domaine] += 1

        with st.expander("🔍 Détails des points par domaine"):
            domaine_named = {
                "D1.1": "1️⃣ D1.1 - Langue française à l'oral et à l'écrit",
                "D1.2": "2️⃣ D1.2 - Langues étrangères et régionales",
                "D1.3": "3️⃣ D1.3 - Langages mathématiques, scientifiques et informatiquese",
                "D1.4": "4️⃣ D1.4 - Langage des arts et du corps",
                "D2": "5️⃣ D2 - Les méthodes et outils pour apprendre",
                "D3": "6️⃣ D3 - La formation de la personne et du citoyen",
                "D4": "7️⃣ D4 - Les systèmes naturels et les systèmes techniques",
                "D5": "8️⃣ D5 - Les représentations du monde et l'activité humaine"
            }
            # Iterate through sorted domain points to display them with friendly names
            for domaine, points in sorted(total_points_par_domaine.items(), key=lambda item: item[0]):
                moyenne = points / nombre_acquisitions_par_domaine[domaine]
                niveau_maitrise = arrondir_maitrise(moyenne)  # Utilise la fonction d'arrondi au niveau de maîtrise supérieur
                points_maitrise = bareme_points[niveau_maitrise]
                total_arrondi += points_maitrise
                st.metric(domaine_named.get(domaine, domaine), f"{points_maitrise} points / 50 points")

        # Calcul et affichage de la moyenne totale des points
        total_points = sum(total_points_par_domaine.values())
        nombre_total_acquisitions = sum(nombre_acquisitions_par_domaine.values())
        moyenne_totale = total_points / nombre_total_acquisitions if nombre_total_acquisitions != 0 else 0
        niveau_maitrise_totale = moyenne_a_maitrise(moyenne_totale)

        # Verifier si c'est un trimestre ou toute l'année
        if periode == "Contrôle Continu (Toute l'année)":
            st.metric("📁 Points du controle continu (*environ*)", f"{total_arrondi} / 400 points")
