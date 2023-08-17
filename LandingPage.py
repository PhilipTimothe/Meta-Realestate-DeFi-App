import streamlit as st
import random
import uuid


# Create fake data
# List of example data for different fields
@st.cache_data
def createFakeData():
    images = [
        "Images/house 1.webp",
        "Images/house 2.webp",
        "Images/house 3.webp",
        "Images/house 4.webp",
        "Images/house 5.webp",
        "Images/house 6.webp",
    ]
    prices = [250000, 320000, 180000, 420000, 550000]
    bedroom_counts = [3, 4, 2, 5, 3]
    bathroom_counts = [2, 3, 2, 4, 2]
    street_addresses = [
        "123 Main St",
        "456 Elm Ave",
        "789 Oak Ln",
        "567 Maple Rd",
        "890 Pine Blvd",
    ]
    cities = ["Springfield", "Meadowville", "Riverside", "Greenville", "Hillside"]
    states = ["CA", "NY", "TX", "FL", "IL"]
    zip_codes = ["12345", "67890", "45678", "23456", "78901"]

    # Generate a list of fake home data
    num_homes = 6
    fake_home_data = []

    for i in range(num_homes):
        home = {
            "image": random.choice(images),
            "price": random.choice(prices),
            "bedrooms": random.choice(bedroom_counts),
            "bathrooms": random.choice(bathroom_counts),
            "street_address": random.choice(street_addresses),
            "city": random.choice(cities),
            "state": random.choice(states),
            "zip_code": random.choice(zip_codes),
        }
        fake_home_data.append(home)

    return fake_home_data


homes = createFakeData()
# ..........................................................................


def wallet_page():
    st.title("Meta RE")

    # placeholder variable that allows for dynamic rendering of objects
    placeholder = st.empty()

    # User wallet address input
    wallet_address = placeholder.text_input(
        "Please enter your wallet address to enter site.", key="1"
    )

    # create criteria for wallet address
    # if wallet address correct send to next page
    if len(wallet_address) > 0:
        tab1, tab2, tab3 = placeholder.tabs(["Browse", "Buy", "Sell"])

        with tab1:
            # Print the generated fake home data
            col1, col2, col3 = st.columns(3)
            columns = [col1, col2, col3]
            counter = 0
            for home in homes:
                with columns[counter]:
                    with st.container():
                        st.image(home["image"], width=200)
                        st.subheader(f"${home['price']:,}")
                        st.caption(f"{home['bedrooms']} bed, {home['bathrooms']} bath")
                        st.caption(
                            f"{home['street_address']}, {home['city']}, {home['state']} {home['zip_code']}"
                        )
                if counter < 2:
                    counter += 1
                else:
                    counter = 0

        with tab2:
            st.header("A dog")
            st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

        with tab3:
            col1, col2 = st.columns([1.55, 3])
            with st.container():
                with col1:
                    st.text("Property Porfolio")
                    for home in homes:
                        keys = str(uuid.uuid1())
                        with st.form(key=keys):
                            st.image(home["image"], width=200)
                            st.caption(
                                f"{home['bedrooms']} bed, {home['bathrooms']} bath"
                            )
                            st.caption(
                                f"{home['street_address']}, {home['city']}, {home['state']} {home['zip_code']}"
                            )
                            submit_button = st.form_submit_button(label="List")


wallet_page()
