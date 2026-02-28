import streamlit as st
import requests
import json
import os

# --- Configurations ---
st.set_page_config(
    page_title="UniHelp - Assistant Administratif IIT/NAU",
    page_icon="🎓",
    layout="wide"
)

# Replace with your actual backend URL if deployed separately
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Custom Styling ---
st.markdown("""
<style>
    .source-box {
        font-size: 0.85em;
        padding: 8px;
        background-color: #f0f2f6;
        border-radius: 5px;
        margin-top: 5px;
        color: #31333f;
    }
    .main-header {
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/university.png", width=60)
    st.title("UniHelp")
    st.markdown("Assistant virtuel pour l'administration de l'IIT/NAU Tunisia.")
    
    st.divider()
    
    st.markdown("### Statistiques")
    try:
        res = requests.get(f"{API_URL}/documents")
        if res.status_code == 200:
            stats = res.json()
            st.metric("Documents indexés", stats.get("total_chunks", 0))
    except Exception:
        st.warning("API non connectée.", icon="⚠️")

# --- Application State ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Bonjour ! Je suis UniHelp. Comment puis-je vous aider avec vos démarches administratives aujourd'hui ?"}]


# --- Main Layout ---
tab1, tab2, tab3 = st.tabs(["💬 Assistant Assistant", "✉️ Générateur d'Email", "📊 Dashboard Admin"])

# ==========================================
# TAB 1: Chatbot (RAG)
# ==========================================
with tab1:
    st.markdown("<h2 class='main-header'>Questions Administratives</h2>", unsafe_allow_html=True)
    st.markdown("Posez vos questions sur les inscriptions, scolarité, bourses, etc.")
    
    # Display chat messages from history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("Voir les sources"):
                    for src in msg["sources"]:
                        file_name = src.get('file', 'N/A')
                        dept = src.get('department', 'N/A')
                        date = src.get('date', 'N/A')
                        st.markdown(f"<div class='source-box'>📄 <b>Fichier:</b> {file_name} <br> 🏛️ <b>Dép:</b> {dept} <br> 📅 <b>Date:</b> {date}</div>", unsafe_allow_html=True)

    # React to user input
    if prompt := st.chat_input("Ex: Comment faire la réinscription ?"):
        # Add user message to state and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from FastAPI
        with st.chat_message("assistant"):
            with st.spinner("Recherche dans les documents..."):
                try:
                    response = requests.post(f"{API_URL}/ask", json={"question": prompt, "top_k": 4})
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "Erreur lors de la génération de la réponse.")
                        sources = data.get("sources", [])
                        
                        st.markdown(answer)
                        if sources:
                            with st.expander("Voir les sources"):
                                for src in sources:
                                    file_name = src.get('file', 'N/A')
                                    dept = src.get('department', 'N/A')
                                    date = src.get('date', 'N/A')
                                    st.markdown(f"<div class='source-box'>📄 <b>Fichier:</b> {file_name} <br> 🏛️ <b>Dép:</b> {dept} <br> 📅 <b>Date:</b> {date}</div>", unsafe_allow_html=True)
                        
                        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
                    else:
                        st.error(f"Erreur API: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Impossible de contacter le serveur (FastAPI n'est pas lancé).")

# ==========================================
# TAB 2: Email Generator
# ==========================================
with tab2:
    st.markdown("<h2 class='main-header'>Générateur d'Email Officiel</h2>", unsafe_allow_html=True)
    
    # Fetch available templates
    templates = {}
    try:
        res = requests.get(f"{API_URL}/templates")
        if res.status_code == 200:
            templates = res.json().get("templates", {})
    except:
        pass
        
    if not templates:
        st.warning("Impossible de charger les modèles depuis l'API.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 1. Remplissez vos informations")
            selected_type_key = st.selectbox("Type de demande:", options=list(templates.keys()), format_func=lambda x: templates[x])
            
            student_name = st.text_input("Nom & Prénom")
            student_id = st.text_input("Numéro de carte d'étudiant / CIN")
            student_level = st.text_input("Niveau d'étude (ex: 2ème année Ingénieur)")
            additional_info = st.text_area("Informations supplémentaires (Raisons de l'absence, Période de stage, etc...)")
            
            include_context = st.checkbox("Inclure les règles de l'université (Recommandé)", value=True)
            
            student_full_info = f"Nom: {student_name}\nID: {student_id}\nNiveau: {student_level}\nDétails: {additional_info}"
            
            generate_btn = st.button("✨ Générer l'Email", type="primary")
            
        with col2:
            st.markdown("### 2. Aperçu")
            if generate_btn:
                if not student_name or not student_id:
                    st.error("Veuillez remplir au moins votre nom et votre numéro d'étudiant.")
                else:
                    with st.spinner("Génération de l'email en cours..."):
                        # Call API
                        payload = {
                            "template_type": selected_type_key,
                            "student_info": student_full_info,
                            "include_rag_context": include_context
                        }
                        try:
                            # Note: To avoid long times for /generate-email, we map the FastAPI endpoint
                            res = requests.post(f"{API_URL}/generate-email", json=payload)
                            if res.status_code == 200:
                                email_text = res.json().get("email", "")
                                st.text_area("Copiez ce texte:", value=email_text, height=400)
                                st.success("Email généré avec succès !")
                            else:
                                st.error(f"Erreur API: {res.text}")
                        except Exception as e:
                            st.error(f"Erreur de génération: {e}")

# ==========================================
# TAB 3: Analytics (Mock)
# ==========================================
with tab3:
    st.markdown("<h2 class='main-header'>Dashboard Admin</h2>", unsafe_allow_html=True)
    st.info("Cette section est réservée à l'administration de l'université pour analyser les requêtes des étudiants.")
    
    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### Top Thématiques des Questions")
        # Pseudo data for presentation
        chart_data = {
            "Inscriptions": 45,
            "Bourses": 30,
            "Examens & Rattrapage": 15,
            "Conventions de stage": 10
        }
        st.bar_chart(chart_data)
        
    with colB:
        st.markdown("#### Derniers Feedbacks Étudiants")
        st.markdown("⭐ 5/5 - *Réponse très rapide pour l'inscription.*")
        st.markdown("⭐ 4/5 - *J'ai trouvé les dates des vacances.*")
        st.markdown("⭐ 2/5 - *La réponse sur le restaurant universitaire est manquante.*")
        
        st.button("Télecharger le rapport complet (CSV)")
