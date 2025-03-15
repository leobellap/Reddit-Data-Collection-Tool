from functions import extract_data


# Choose subreddit name, name of submission filtering, number of submissions to load
subreddit_name = ""
submission_filters = [""]  # 'top', 'hot' or both
submission_limit = 75
time_filter = ""  # 'all', 'day', 'hour', 'month', 'week', 'year', only for 'top' submission type filter

extract_data(subreddit_name, submission_filters, submission_limit, time_filter)
