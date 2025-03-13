import praw
from datetime import datetime
import configparser
from tqdm import tqdm
import pandas as pd
import re
import os

config = configparser.ConfigParser()
config.read("config.ini")

reddit = praw.Reddit(
    client_id=config.get("reddit", "client_id"),
    client_secret=config.get("reddit", "client_secret"),
    user_agent=config.get("reddit", "user_agent"),
    username=config.get("reddit", "username"),
    password=config.get("reddit", "password"),
    check_for_async=False,
)


def load_data(subreddit_name, submission_filter, submission_limit, time_filter):
    comments = []

    subreddit = reddit.subreddit(subreddit_name)
    subreddit_name = subreddit.display_name

    moderators = []
    for moderator in subreddit.moderator():
        moderators.append(moderator.name)

    if submission_filter == "hot":
        # Получаем список самых обсуждаемых тем за день
        hot_submissions = subreddit.hot(limit=submission_limit)

        # Проходим по всем обсуждаемым темам
        for submission in tqdm(hot_submissions):
            # # Проверяем, что тема была создана за последние 24 часа
            # if submission.created_utc > time.time() - 24 * 60 * 60:

            # Загружаем только те комментарии, которые алгоритмы Reddit считают самыми важными
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

    elif submission_filter == "top":
        # Получаем список самых обсуждаемых тем за выбранный промежуток времени
        top_submissions = subreddit.top(time_filter=time_filter, limit=submission_limit)

        # Проходим по всем обсуждаемым темам
        for submission in tqdm(top_submissions):
            # Загружаем только те комментарии, которые алгоритмы Reddit считают самыми важными
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


def regex_preprocessing(text):
    # Функции для очистки

    # Замена лишних пробелов на один пробел
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_df(df, moderators):
    df["submission_date"] = pd.to_datetime(df.submission_date, unit="s")
    df["comment_date"] = pd.to_datetime(df.comment_date, unit="s")

    df = df.drop_duplicates(keep=False, subset=["comment_text"])

    df = df.loc[~df["submission_author"].astype("string").isin(moderators)]
    df = df.loc[~df["comment_author"].astype("string").isin(moderators)]

    df["comment_text"] = df["comment_text"].apply(regex_preprocessing)
    df["submission_selftext"] = df["submission_selftext"].apply(regex_preprocessing)
    df["submission_title"] = df["submission_title"].apply(regex_preprocessing)

    return df.reset_index(drop=True)


def save_data(df, subreddit_name, submission_filter, time_filter):
    # Сохраним данные в csv
    current_date = datetime.now().strftime("%Y_%m_%d")

    # Define the path where the file will be saved
    if submission_filter == "top":
        file_path = f"csvs/{submission_filter}/{subreddit_name}_{submission_filter}_{time_filter}_{current_date}.csv"
    else:
        file_path = f"csvs/{submission_filter}/{subreddit_name}_{submission_filter}_{current_date}.csv"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the dataframe to the CSV file
    df.to_csv(file_path, index=False)
