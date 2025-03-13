import pandas as pd
from functions import load_data, clean_df, save_data


# Choose subreddit name, name of submission filtering, number of submissions to load
subreddit_name = ""
submission_filters = [""]  # 'top', 'hot'
submission_limit = 75
time_filter = ""  # 'all', 'day', 'hour'

for submission_filter in submission_filters:
    # Parse data
    comments, moderators = load_data(
        subreddit_name=subreddit_name,
        submission_filter=submission_filter,
        submission_limit=submission_limit,
        time_filter=time_filter,
    )

    # Create DataFrame to store parsed data
    df = pd.DataFrame(
        comments,
        columns=[
            "submission_date",
            "submission_score",
            "submission_upvote_ratio",
            "submission_title",
            "submission_selftext",
            "submission_author",
            "comment_date",
            "comment_score",
            "comment_author",
            "comment_text",
            "comment_is_submitter",
            "submission_permalink",
            "submission_url",
        ],
    )

    # Clean data in DataFrame
    df = clean_df(df, moderators)

    # Save DataFrame to csv file
    save_data(df, subreddit_name, submission_filter, time_filter)
