# Reddit Data Collection and Analysis

This project collects and processes data from a specified Reddit subreddit. The data is filtered based on submission filters, such as "top" or "hot", and the number of submissions can be limited. The collected data is then cleaned and saved into a CSV file (and optionally into a DuckDB database).

## Features

- **Data Collection**: Fetches data from Reddit posts and comments.
- **Flexible Filters**: Allows filtering by submission type ("top", "hot") and time frame (e.g., "all", "day", "hour", supported only for "top" submission type filtering).
- **Data Cleaning**: Cleans the collected data for easier analysis.
- **Data Saving**: Saves the processed data to CSV or DuckDB.

## Requirements

Before running the project, ensure you have **PDM** installed. Once PDM is installed, you can set up the environment and install dependencies by running:

```bash
pdm install
```

This will install the required dependencies, including `pandas`, `praw`, and any custom packages defined in `pyproject.toml`.

## Files

- **main.py**: The main script for data collection, processing, and saving.
- **functions.py**: Contains functions to load, clean, and save the data. Ensure this file is in the same directory as `main.py`.
- **pyproject.toml**: The configuration file where dependencies are listed.

## Setup

1. **Edit Configuration**:  
   In `main.py`, configure the following variables:
   
   - `subreddit_name`: Set the name of the subreddit from which you want to fetch data.
   - `submission_filters`: List the types of posts you want to collect, such as `["top"]`, `["hot"]`, or other available filters.
   - `submission_limit`: Set the maximum number of submissions to retrieve.
   - `time_filter`: Optionally filter submissions by time frame, such as `"all"`, `"day"`, or `"hour"`. Only available for `["top"]` submission type filter.

   Example configuration:

   ```python
   subreddit_name = "learnpython"
   submission_filters = ["top"]  # Retrieve only 'top' posts
   submission_limit = 100       # Limit to 100 submissions
   time_filter = "all"          # No time filter
   ```

2. **Run the Script**:  
   After editing the configuration, run the script with:

   ```bash
   python main.py
   ```

   This will fetch data from the specified subreddit and save it to a CSV file.

## Functions

The main script relies on the following functions:

- `load_data`: Loads data from the specified subreddit based on the provided filters.
- `clean_df`: Cleans the DataFrame.
- `save_data`: Saves the cleaned DataFrame to a CSV file.
- `save_data_to_duckdb`: Optionally saves the DataFrame to a DuckDB database for further analysis.

## Example Output

The cleaned data will be saved as a CSV file in the format:

```
{subreddit_name}_{submission_filter}_{time_filter}_{current_date}.csv
```

or

```
{subreddit_name}_{submission_filter}_{current_date}.csv
```

For example:

```
learnpython_top_all_2025_03_14.csv
```

## Optional: Save Data to DuckDB

Uncomment the following line in `main.py` to save data to a DuckDB database:

```python
# save_data_to_duckdb(df, subreddit_name, submission_filter, time_filter)
```

## Contributing

If you would like to contribute to this project, feel free to fork the repository, submit a pull request, or open an issue with suggestions or improvements.

## License

This project is licensed under the MIT License.
