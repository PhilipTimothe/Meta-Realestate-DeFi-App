import streamlit as st
from web3 import Web3
import json
from types import SimpleNamespace


def adminSignin(contract, contract_owner, w3):
    st.title("Admin Signin")
    owner_address = st.text_input("Enter admin address")
    if st.button("Sign In") and (owner_address == contract_owner):
        st.success(f"Connected to {contract_owner}")
        return owner_address
    return None
    # create error for wrong address


def confirmStatus(contract, contract_owner, w3):
    st.session_state.owner_address = contract_owner
    contract.functions.getPendingTokens().transact(
        {"from": st.session_state.owner_address}
    )
    tx_hash = contract.events.pendingTokens.create_filter(fromBlock=0).get_all_entries()
    data = Web3.to_json(tx_hash[-1])
    x = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
    token = x.args.tokens

    status = {"Approved": 1, "Rejected": 2}

    for i in range(len(x.args.tokens)):
        col1, col2 = st.columns([0.7, 3])
        with col1:
            form = st.form(key=f"{token[i]}")
            form.write(f"Property Id: {token[i]}")
            approved = form.form_submit_button("Approved")
            rejected = form.form_submit_button("Rejected")
            if approved:
                contract.functions.setTokenStatus(
                    token[i], status["Approved"]
                ).transact({"from": st.session_state.owner_address})
            if rejected:
                contract.functions.setTokenStatus(
                    token[i], status["Rejected"]
                ).transact({"from": st.session_state.owner_address})
