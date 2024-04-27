import asyncio

from api import fetch_data
from config import API_PARAMS, API_URL, CSV_OUTPUT_PATH, IMG_DIR, NUM_CALLS
from data_processing import (
    append_data_to_csv,
    convert_json_to_trash_nothing_post,
    initialize_csv_with_headers,
    load_and_process_data,
)

from PIL import Image

import streamlit as st
import plotly.express as px
from visualization import create_countplot, create_histogram


async def main():

    posts = []

    # pull data from API and append to posts
    for idx in range(NUM_CALLS):
        await asyncio.sleep(1)
        task = fetch_data(API_URL, API_PARAMS, idx + 1)
        posts.append(task)

    results = await asyncio.gather(*posts, return_exceptions=True)

    for idx in range(NUM_CALLS):
        for result in results[idx]["posts"]:
            # if error, print error
            if isinstance(result, Exception):
                print(result)
                st.error(f"Error: {result}")

            else:
                # transform JSON to dataclas
                auction = convert_json_to_trash_nothing_post(result)

                # create csv w/ headers if csv does not exist
                initialize_csv_with_headers(CSV_OUTPUT_PATH, auction.keys())

                # append new data to CSV
                append_data_to_csv(CSV_OUTPUT_PATH, auction)

    
    ### -- Create dashboard with visualizations -- ###
    
    # setup dashboard configuration
    im = Image.open(IMG_DIR / "recycle.png")
    st.set_page_config(
        page_title="Trash Nothing Dashboard",
        page_icon=im,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # read and process dataset
    df = load_and_process_data(CSV_OUTPUT_PATH, "post_date", "expiry_date")

    # create distribution of # of days that an item is available for pickup
    pickup_days_fig = create_histogram(
        df["days_available_for_pickup"], title="Days Available for Pickup Distribution"
    )

    # create a count plot for 'outcome'
    outcome_fig = create_countplot(df, variable="outcome", title="Trash Post Outcome")

    # create a count plot showing the level of interest
    interest_fig = create_countplot(df, variable="reply_measure", title="Level of Interest in Trash")

    # display figures
    st.plotly_chart(pickup_days_fig)
    st.plotly_chart(outcome_fig)
    st.plotly_chart(interest_fig)



if __name__ == "__main__":
    asyncio.run(main())
