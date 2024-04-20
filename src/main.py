import asyncio

from config import (
    API_URL, API_PARAMS, API_HEADERS, CSV_OUTPUT_PATH, NUM_CALLS
)
from api import fetch_data
from data_processing import (
    convert_json_to_trash_nothing_post,
    initialize_csv_with_headers,
    append_data_to_csv,
)

from pprint import pprint


async def main():
    
    posts = []
    
    # pull data from API and append to posts
    for _ in range(NUM_CALLS):
        await asyncio.sleep(1)
        task = fetch_data(API_URL, API_PARAMS, API_HEADERS)
        posts.append(task)
        API_PARAMS["page"] += 1

    results = await asyncio.gather(*posts, return_exceptions=True)

    for idx in range(NUM_CALLS):
        for result in results[idx]["posts"]:
            # if error, print error
            if isinstance(result, Exception):
                print(result)
            
            else:        
                # transform JSON to dataclas
                auction = convert_json_to_trash_nothing_post(result)

                # create csv w/ headers if csv does not exist
                initialize_csv_with_headers(CSV_OUTPUT_PATH, auction.keys())

                # append new data to CSV
                append_data_to_csv(CSV_OUTPUT_PATH, auction)
        

if __name__ == "__main__":
    asyncio.run(main())
