import streamlit as st
from web3 import Web3
import json
from types import SimpleNamespace


def getAllSaleProperties(contract, wallet_address, w3):
    st.session_state.wallet_address = wallet_address
    contract.functions.getTokensForSale().transact(
        {"from": st.session_state.wallet_address, "gas": 1000000}
    )
    # filter properties and build functionality
    filter = contract.events.approvedTokens.create_filter(fromBlock=0)
    for i in filter.get_all_entries():
        st.write(dict(i))
    # data = Web3.to_json(tx_hash)
    # x = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
    # token = x.args.tokens

    # Create columns for approved properties
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]
    counter = 0
    # for home in homes:
    #     with columns[counter]:
    #         with st.container():
    #             st.image(home["image"], width=200)
    #             st.subheader(f"${home['price']:,}")
    #             st.caption(f"{home['bedrooms']} bed, {home['bathrooms']} bath")
    #             st.caption(
    #                 f"{home['street_address']}, {home['city']}, {home['state']} {home['zip_code']}"
    #             )
    #     if counter < 2:
    #         counter += 1
    #     else:
    #         counter = 0

    # Add a back button to navigate to the actions page
    if st.button("Back to Actions"):
        # End the minting session
        st.session_state.page = "actions"
        st.experimental_rerun()
