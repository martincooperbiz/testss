import streamlit as st
import json
import requests
import os
import pandas as pd
from datetime import datetime
import pytz

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
        # Assuming 1 kg of chicken equals 4 pieces
        return quantity * 4
    elif unit == "KG":
        # Assuming 1 piece of chicken weighs 0.25 kg
        return quantity * 0.25

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
        st.write(df)

# Function to show the form
def show_form():
    st.subheader("Formulaire de Commande")

    produit_input = st.text_input("Produit", "", key="produit_input")
    
    st.subheader("Unité")
    unite_options = ["Pcs", "KG"]
    unite_selected = st.radio("Choisir une unité", unite_options)

    st.subheader("Dépôt")
    depot_options = ["Frais", "Surgelé"]
    depot_selected = st.radio("Choisir un dépôt", depot_options)

    quantite_input = st.number_input("Quantité", 1, key="quantite_input")
    conditionnement_input = st.text_input("Conditionnement", "", key="conditionnement_input")
    autres_specifications_input = st.text_area("Autres spécifications", "", key="autres_specifications_input")

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
        
        # Calculate estimate
        estimate = calculate_estimate(unite_selected, quantite_input)
        
        # Display estimate
        st.write(f"Estimation: {estimate} {'KG' if unite_selected == 'Pcs' else 'Pcs'}")
        
        # Add data to order history
        st.session_state.order_history.append(data)
        save_order_history(st.session_state.order_history, st.session_state.username)  # Save order history to user's file

if __name__ == "__main__":
    main()
