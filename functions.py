import praw
from datetime import datetime
import configparser
from tqdm import tqdm
import pandas as pd
import re
import duckdb
import os

# Import Reddit App data from config file
config = configparser.ConfigParser()
config.read("config.ini")

# Initialize PRAW
reddit = praw.Reddit(
    client_id=config.get("reddit", "client_id"),
    client_secret=config.get("reddit", "client_secret"),
    user_agent=config.get("reddit", "user_agent"),
    username=config.get("reddit", "username"),
    password=config.get("reddit", "password"),
    check_for_async=False,
)


# Function to parse data
def load_data(subreddit_name, submission_filter, submission_limit, time_filter):
    comments = []

    subreddit = reddit.subreddit(subreddit_name)
    subreddit_name = subreddit.display_name

    # Get moderator's names to filter their responses and submissions
    moderators = []
    for moderator in subreddit.moderator():
        moderators.append(moderator.name)

    if submission_filter == "hot":
        hot_submissions = subreddit.hot(limit=submission_limit)

        for submission in tqdm(hot_submissions):
            # # Choose a timeframe if you need
            # if submission.created_utc > time.time() - 24 * 60 * 60:

            # Parse only the most important comments to reduce the number of requests
            submission.comments.replace_more(limit=0)

            for comment in submission.comments.list():
                # Choose data you want to extract from comments and submissions
                comment_info = [
                    submission.created_utc,
                    submission.score,
                    submission.upvote_ratio,
                    submission.title,
                    submission.selftext,
                    submission.author,
                    comment.created_utc,
                    comment.score,
                    comment.author,
                    comment.body,
                    comment.is_submitter,
                    submission.permalink,
                    submission.url,
                ]
                comments.append(comment_info)

    elif submission_filter == "top":
        top_submissions = subreddit.top(time_filter=time_filter, limit=submission_limit)

        for submission in tqdm(top_submissions):
            submission.comments.replace_more(limit=0)

            for comment in submission.comments.list():
                comment_info = [
                    submission.created_utc,
                    submission.score,
                    submission.upvote_ratio,
                    submission.title,
                    submission.selftext,
                    submission.author,
                    comment.created_utc,
                    comment.score,
                    comment.author,
                    comment.body,
                    comment.is_submitter,
                    submission.permalink,
                    submission.url,
                ]
                comments.append(comment_info)

    return comments, moderators


# Function for in-comment cleaning
def preprocess_data(text):
    # Add data preprocessing logic here

    # Delete unnecessary whitespaces
    text = re.sub(r"\s+", " ", text)

    # Remove any leading and trailing whitespaces
    return text.strip()


# Process DataFrame with parsed data
def clean_df(df, moderators):
    df["submission_date"] = pd.to_datetime(df.submission_date, unit="s")
    df["comment_date"] = pd.to_datetime(df.comment_date, unit="s")

    df = df.drop_duplicates(keep=False, subset=["comment_text"])

    df = df.loc[~df["submission_author"].astype("string").isin(moderators)]
    df = df.loc[~df["comment_author"].astype("string").isin(moderators)]

    df["comment_text"] = df["comment_text"].apply(preprocess_data)
    df["submission_selftext"] = df["submission_selftext"].apply(preprocess_data)
    df["submission_title"] = df["submission_title"].apply(preprocess_data)

    return df.reset_index(drop=True)


# Save DataFrame to the CSV file
def save_data(df, subreddit_name, submission_filter, time_filter):
    current_date = datetime.now().strftime("%Y_%m_%d")

    # Define the path where the file will be saved
    if submission_filter == "top":
        file_path = f"csvs/{submission_filter}/{subreddit_name}_{submission_filter}_{time_filter}_{current_date}.csv"
    else:
        file_path = f"csvs/{submission_filter}/{subreddit_name}_{submission_filter}_{current_date}.csv"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    df.to_csv(file_path, index=False)


# Save DataFrame to DuckDB
def save_data_to_duckdb(df, subreddit_name, submission_filter, time_filter):
    # Define the DuckDB file path
    db_file_path = "parsed_data.db"

    # Connect to the DuckDB database
    conn = duckdb.connect(db_file_path)

    # Create a table name based on the subreddit and filter to ensure uniqueness
    if submission_filter == "top":
        table_name = f"{subreddit_name}_{submission_filter}_{time_filter}"
    else:
        table_name = f"{subreddit_name}_{submission_filter}"

    # Check if the table exists in the database
    table_exists = conn.execute(
        f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
    ).fetchone()[0]

    if table_exists == 0:
        # Table does not exist, create it and insert the data
        conn.execute(
            f"CREATE TABLE {table_name} AS SELECT * FROM df"
        )  # Creates an empty table with the same structure
        conn.sql(f"INSERT INTO {table_name} SELECT * FROM df")
        print(f"Table {table_name} created and data inserted.")
    else:
        # Table exists, append the data
        conn.sql(f"INSERT INTO {table_name} SELECT * FROM df")
        print(f"Data appended to existing table {table_name}.")

    # Close the connection
    conn.close()
