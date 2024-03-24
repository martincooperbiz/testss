import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# Define the webhook URL
WEBHOOK_URL = "https://49win8x85gkbzcpq5ze9dr.streamlit.app/webhook/a6554989-c70a-486c-a7fe-52790cf59cea"

# Function to get current date and time in Morocco (Rabat) timezone
def get_current_datetime():
    tz = pytz.timezone('Africa/Casablanca')
    current_time = datetime.now(tz)
    return current_time.strftime('%Y-%m-%d %H-%M-%S')

# Function to calculate the estimate based on unit and quantity
def calculate_estimate(unit, quantity):
    if unit == "Pcs":
        return quantity * 1.5, "KG"
    elif unit == "KG":
        return quantity * 0.70, "Pcs"

def main():
    st.title("Commande")

    # Check if user is logged in
    if "username" not in st.session_state:
        st.session_state.username = None

    # Check if user has order history
    if "order_history" not in st.session_state:
        st.session_state.order_history = []

    # Login Section
    if st.session_state.username is None:
        st.subheader("Connexion")
        username = st.text_input("Nom d'utilisateur", key="login_username_input")
        password = st.text_input("Mot de passe", type="password", key="login_password_input")
        login_button = st.button("Se connecter")

        if login_button:
            # For simplicity, let's assume authentication always succeeds
            st.session_state.username = username

    # Show form if logged in
    if st.session_state.username:
        st.write(f"Connecté en tant que: {st.session_state.username}")
        show_form()

        # Show order history
        st.subheader("Historique des commandes")
        df = pd.DataFrame(st.session_state.order_history)
        if not df.empty:
            df = df.drop(columns=["Estimation", "Estimation_Unit"], errors="ignore")
            st.write(df)

# Function to show the form
def show_form():
    st.title("Commande de Produits")
    st.write("Veuillez remplir le formulaire ci-dessous pour passer votre commande.")

    produit_input = st.text_input("Nom du Produit", "", key="produit_input")
    
    col1, col2 = st.columns(2)
    with col1:
        unite_selected = st.radio("Unité", ["Pcs", "KG"], key="unit_input")
    with col2:
        depot_selected = st.radio("Dépôt", ["Frais", "Surgelé"], key="depot_input")

    quantite_input = st.number_input("Quantité", 1, key="quantite_input")

    estimate, estimate_unit = calculate_estimate(unite_selected, quantite_input)
    st.write(f"Estimation: {estimate} {estimate_unit}")

    conditionnement_input = st.text_input("Conditionnement", "", key="conditionnement_input")
    autres_specifications_input = st.text_area("Autres Spécifications", "", key="autres_specifications_input")

    if st.button("ENVOYER"):
        data = {
            "Date et heure": get_current_datetime(),
            "Produit": produit_input,
            "Unité": unite_selected,
            "Quantité": quantite_input,
            "Dépôt": depot_selected,
            "Conditionnement": conditionnement_input,
            "Autres spécifications": autres_specifications_input,
            "Username": st.session_state.username
        }
        
        # Send data to webhook
        response = requests.post(WEBHOOK_URL, json=data)
        
        # Save data to order history
        st.session_state.order_history.append(data)

        # Save data as CSV file
        filename = f"{data['Username']}_{data['Date et heure']}.csv"
        df = pd.DataFrame([data])
        df.to_csv(filename, index=False)

if __name__ == "__main__":
    main()
