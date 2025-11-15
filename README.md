# Anvisul – Flask Backend (Data Science Skill Based Mini Project)
This backend processes raw CSV data and turns it into structured, cleaned, and statistically analyzed output. It accepts CSV-like input from the frontend, converts it into JSON records, infers correct data types, handles missing values, removes duplicates, and returns complete summary statistics that can be directly used in any application.

This project is a Python Flask-based backend service that takes raw CSV-like data (sent as JSON records) and converts it into a structured, analyzed, and cleaned dataset. It solves a simple but common issue: most people do not know how to manually process inconsistent CSV files, fix null values, detect the right data types, remove duplicates, or compute meaningful statistics. Users normally need Excel, Pandas, or scripts to do this. With this API, they can send the raw data and immediately get a complete summary, inferred column types, descriptive statistics, and a cleaned dataset in a format ready to use in any frontend or system.

The backend exposes two main endpoints. The first one accepts raw data and analyzes it. It identifies null-like values, converts them into proper missing entries, infers column types automatically (numeric, datetime, or text), and computes useful statistical information such as mean, median, mode, standard deviation, min, max, and record counts. It also generates a pandas describe output and returns a JSON-safe cleaned dataset with nulls properly handled. The second endpoint focuses on cleaning: it removes duplicate rows, drops rows containing any missing values, re-evaluates data types, and returns updated statistics alongside the cleaned dataset.

Anyone who wants to use this project can simply clone the code and install the necessary dependencies. Python and pip are required. After installing the packages (Flask, Flask-CORS, pandas, numpy), the server can be started directly. Once running, the API accepts POST requests with a list of JSON objects representing CSV rows. Any frontend or script can call these endpoints to analyze or clean the data. The output is always clean JSON that can be displayed in tables, charts, or used for further processing.

The workflow is straightforward: you send the data, the server analyzes it, and you get structured insights. This saves users from writing manual scripts, cleaning data by hand, or dealing with broken CSV files. It also ensures the output is consistent and statistical information is always available. This is useful for dashboard builders, data-entry tools, automation platforms, or anyone dealing with uploaded CSV files.

To run the project locally, install the dependencies:
```bash
pip install flask flask-cors pandas numpy
```
Then start the server:
```bash
python app.py
```
The server will run on port 5000. A basic GET request to / confirms it's running. To analyze data, send a POST request to /analyze with a JSON list. To clean data, send a POST request to /clean with the same format.

The backend is deployed on Render, and the frontend (built in Next.js 16) communicates with it directly. Users never call the API manually. When they upload a CSV or trigger an action on the frontend, the Next.js app sends a request to this Render server, receives the analyzed or cleaned data, and displays the results on the UI. In short, the frontend is the entry point for users, and this backend works completely in the background to process whatever data the frontend sends.
[Live Link](https://anvisul.vercel.app/)
