import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('medcore.db')


vitals = pd.read_sql_query("SELECT * FROM chat_messages;  ", conn)
print(vitals.to_string())

