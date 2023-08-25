import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import uuid
from adminSignin import adminSignin, confirmStatus
from buyProperty import getAllSaleProperties

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))


@st.cache(allow_output_mutation=True)
def load_contract():
    # Load the contract’s ABI details next
    with open(Path("contracts/compiled/RealEstateToken_abi.json")) as f:
        real_estate_token_abi = json.load(f)

    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    contract = w3.eth.contract(address=contract_address, abi=real_estate_token_abi)

    return contract


# load contract
contract = load_contract()
# collect all available account wallet addresses
accounts = w3.eth.accounts


# Function fetching balances
def fetch_balances(wallet_address):
    mre_balance = w3.eth.get_balance(wallet_address)
    return mre_balance


# Display fetched balances
def display_balances(mre_balance, WalletAddress):
    """Display the MRE balance"""
    st.subheader("Your Balance")
    st.write(f"Wallet Address: {WalletAddress}")
    st.write(f"MREs: {mre_balance}")


# Connect User wallet address for application access
def connect_wallet():
    st.subheader("Connect Your Wallet")

    wallet_address = st.selectbox("Enter your Ethereum address", options=accounts)
    # wallet_address = st.text_input("Enter your Ethereum address:")
    connect_button = st.button("Connect")

    if connect_button and wallet_address:
        st.success(f"Connected to {wallet_address}")
        return wallet_address
    return None


# Main functionality architecture of application!!
def main():
    st.title("Real Estate Token Platform")

    # Page navigation
    page = st.session_state.page if "page" in st.session_state else "connect_wallet"

    # if connection of wallet is successful save in state
    if page == "connect_wallet":
        st.session_state.wallet_address = connect_wallet()
        if st.session_state.wallet_address:
            st.session_state.page = "actions"
            st.experimental_rerun()

    elif page == "actions":
        mre_balance = fetch_balances(st.session_state.wallet_address)
        display_balances(mre_balance, st.session_state.wallet_address)
        user_actions()

    elif page == "mint":
        mre_balance = fetch_balances(st.session_state.wallet_address)
        display_balances(mre_balance, st.session_state.wallet_address)
        mint_property()

    elif page == "buy":
        mre_balance = fetch_balances(st.session_state.wallet_address)
        display_balances(mre_balance, st.session_state.wallet_address)
        getAllSaleProperties(contract, st.session_state.wallet_address, w3)

    elif page == "portfolio":
        mre_balance = fetch_balances(st.session_state.wallet_address)
        display_balances(mre_balance, st.session_state.wallet_address)
        see_portfolio()

    elif page == "admin":
        contract_owner = "0x06C63f1F9C4c908F51b3106B78b84b1c1c6F5985"
        st.session_state.owner_address = adminSignin(contract, contract_owner, w3)
        if st.session_state.owner_address:
            st.session_state.page = "status"
            st.experimental_rerun()

    elif page == "status":
        confirmStatus(contract, st.session_state.owner_address, w3)
        # Add a back button to navigate to the actions page
        if st.button("Back to Actions"):
            # End the minting session
            st.session_state.page = "actions"
            st.experimental_rerun()


# Main page
def user_actions():
    st.subheader("Choose an Action")

    if st.button("Mint"):
        st.session_state.page = "mint"
        st.experimental_rerun()

    if st.button("Buy"):
        st.session_state.page = "buy"
        st.experimental_rerun()

    if st.button("See Portfolio"):
        st.session_state.page = "portfolio"
        st.experimental_rerun()

    if st.button("Admin"):
        st.session_state.page = "admin"
        st.experimental_rerun()


# Mint new properties functionality
def mint_property():
    st.subheader("Mint a New RE Token")

    # Initialize or retrieve the descriptions list
    if "descriptions" not in st.session_state:
        st.session_state.descriptions = []

    # Check if this is a fresh minting session or an ongoing one
    if "mint_session" not in st.session_state:
        st.session_state.mint_session = str(
            uuid.uuid4()
        )  # Assign a unique id for this minting session
    else:
        st.session_state.mint_session = (
            st.session_state.mint_session
        )  # Use the existing minting session id

    real_world_address = st.text_input(
        "Enter the real-world address associated with this RE:"
    )
    description = st.text_input("Brief description of the property:")

    uploaded_image = st.file_uploader(
        "Upload an image of the property", type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:
        # Create a unique filename for each image
        image_path = os.path.join(
            os.getcwd(), f"{st.session_state.mint_session}_{uploaded_image.name}.png"
        )

        if not os.path.exists(image_path):
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getvalue())

        st.image(uploaded_image, caption="Uploaded Image.", width=200)

    mint_button = st.button("Mint RE Token")
    if mint_button and real_world_address and description and uploaded_image:
        # create blockchain transaction functionality
        tokenURI = f"{real_world_address}, {description}"
        tx_hash = contract.functions.registerHouse(tokenURI).transact(
            {"from": st.session_state.wallet_address, "gas": 1000000}
        )
        # Append the description to our descriptions list
        st.session_state.descriptions.append(
            {
                "address": real_world_address,
                "description": description,
                "image_path": image_path,
            }
        )

        # send completion notice and reciept of the transaction
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        st.success(f"Successfully minted RE for address: {real_world_address}")
        st.write(dict(receipt))

    # Add a back button to navigate to the actions page
    if st.button("Back to Actions"):
        # End the minting session
        del st.session_state.mint_session
        st.session_state.page = "actions"
        st.experimental_rerun()


# Connect to blockchain / solidity contract for resulting properties
# Add status to each property object
def see_portfolio():
    st.subheader("Your Property Portfolio")

    # Retrieve the descriptions list or initialize it if not present
    if "descriptions" not in st.session_state:
        st.session_state.descriptions = []

    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]
    counter = 0
    for idx, property in enumerate(st.session_state.descriptions):
        current_column = columns[counter]

        with current_column.container():
            # Use the selected column to display the property
            current_column.image(
                property["image_path"], caption="Property Image", width=200
            )
            current_column.write(f"Address: {property['address']}")
            current_column.write(f"Token ID: {idx}")
            current_column.write(f"Description: {property['description']}")

            # If the button is clicked, show a number input for the price
            if current_column.button(f"List for Sale", key=f"list_for_sale_{idx}"):
                current_column.number_input("List Price", key=f"price_{idx}")

        # Update the counter for columns
        if counter < 2:
            counter += 1
        else:
            counter = 0

    # Add a back button to navigate to the actions page
    if st.button("Back to Actions"):
        st.session_state.page = "actions"
        st.experimental_rerun()


# Run main function to start the app
if __name__ == "__main__":
    main()
