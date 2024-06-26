import streamlit as st
import json
import requests
import os
import pandas as pd
from datetime import datetime
import pytz

# Define the webhook URL
WEBHOOK_URL = "https://hook.eu2.make.com/t2bw8tqskcutqtak5h60cwwa7mxb431v"

# Function to authenticate user
def authenticate(username, password):
    with open('user.json', 'r') as f:
        data = json.load(f)
        users = data["users"]
        for user in users:
            if user["username"] == username and user["password"] == password:
                return True
    return False

# Function to load order history data from JSON file for a specific user
def load_order_history(username):
    try:
        filename = f'order_history_{username}.json'
        with open(filename, 'r') as f:
            order_history = json.load(f)
    except FileNotFoundError:
        order_history = []
    return order_history

# Function to save order history data to JSON file for a specific user
def save_order_history(order_history, username):
    filename = f'order_history_{username}.json'
    with open(filename, 'w') as f:
        json.dump(order_history, f, indent=4)

# Function to get current date and time in Morocco (Rabat) timezone
def get_current_datetime():
    tz = pytz.timezone('Africa/Casablanca')
    current_time = datetime.now(tz)
    return current_time.strftime('%Y-%m-%d %H:%M:%S')


# Function to calculate the estimate based on unit and quantity
def calculate_estimate(unit, quantity):
    if unit == "Pcs":
        # Assuming 1.5 kg of chicken equals 1 pieces
        return quantity * 1.5, "KG"
    elif unit == "KG":
        # Assuming 0.70 piece of chicken weighs 1 kg
        return quantity * 0.70, "Pcs"

def main():
    st.title("Commande")

    # Check if user is logged in
    if "username" not in st.session_state:
        st.session_state.username = None

    # Check if user has order history
    if "order_history" not in st.session_state:
        st.session_state.order_history = load_order_history(st.session_state.username)

    # Login Section
    if st.session_state.username is None:
        st.subheader("Connexion")
        username = st.text_input("Nom d'utilisateur", key="login_username_input")
        password = st.text_input("Mot de passe", type="password", key="login_password_input")
        login_button = st.button("Se connecter")

        if login_button:
            if authenticate(username, password):
                st.session_state.username = username
                st.session_state.order_history = load_order_history(username)  # Load order history for the user
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect")

    # Show form if logged in
    if st.session_state.username:
        st.write(f"Connecté en tant que: {st.session_state.username}")
        show_form()

        # Show order history
        st.subheader("Historique des commandes")
        df = pd.DataFrame(st.session_state.order_history)
        if not df.empty:
            df = df.drop(columns=["Estimation", "Estimation_Unit"], errors="ignore")  # Drop the estimation and its unit columns from display
            st.write(df)

# Function to show the form
def show_form():
    st.title("Commande de Produits")
    st.write("Veuillez remplir le formulaire ci-dessous pour passer votre commande.")

    st.subheader("Produit")
    produit_input = st.text_input("Nom du Produit", "", key="produit_input")
    
    # Layout columns for unit and depot selection
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Unité")
        unite_options = ["Pcs", "KG"]
        unite_selected = st.radio("", unite_options, key="unit_input")
    with col2:
        st.subheader("Dépôt")
        depot_options = ["Frais", "Surgelé"]
        depot_selected = st.radio("", depot_options, key="depot_input")

    st.subheader("Quantité")

    # Quantity input
    quantite_input = st.number_input("", 1, key="quantite_input")

    # Calculate and display estimate
    estimate, estimate_unit = calculate_estimate(unite_selected, quantite_input)
    st.write(f"Estimation: {estimate} {estimate_unit}")

    st.subheader("Conditionnement")
    conditionnement_input = st.text_input("Conditionnement", "", key="conditionnement_input")

    st.subheader("Autres Spécifications")
    autres_specifications_input = st.text_area("Indiquez toutes les autres spécifications ici", "", key="autres_specifications_input")

    # Add other functionalities here if needed

    if st.button("ENVOYER"):
        # Create JSON object with form data
        data = {
            "Date et heure": get_current_datetime(),  # Add current date and time
            "Produit": produit_input,
            "Unité": unite_selected,
            "Quantité": quantite_input,
            "Dépôt": depot_selected,
            "Conditionnement": conditionnement_input,
            "Autres spécifications": autres_specifications_input,
            "Username": st.session_state.username
        }
        
        # Send data to webhook (excluding estimation and its unit)
        data_to_send = {key: value for key, value in data.items() if key not in ["Estimation", "Estimation_Unit"]}
        response = requests.post(WEBHOOK_URL, json=data_to_send)
        
        # Add data to order history (excluding estimation and its unit)
        st.session_state.order_history.append(data_to_send)
        save_order_history(st.session_state.order_history, st.session_state.username)  # Save order history to user's file

if __name__ == "__main__":
    main()
