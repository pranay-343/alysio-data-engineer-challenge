import sqlite3

    # Connect to database
conn = sqlite3.connect('salesforce_data.db')
cursor = conn.cursor()

    # Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Companies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT,
    industry TEXT,
    size TEXT,
    country TEXT,
    created_date TEXT,
    is_customer INTEGER,
    annual_revenue INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Contacts (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    title TEXT,
    company_id TEXT,
    phone TEXT,
    status TEXT,
    created_date TEXT,
    last_modified TEXT,
    FOREIGN KEY (company_id) REFERENCES Companies(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Opportunities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    contact_id TEXT,
    company_id TEXT,
    amount INTEGER,
    stage TEXT,
    product TEXT,
    probability INTEGER,
    created_date TEXT,
    close_date TEXT,
    is_closed INTEGER,
    forecast_category TEXT,
    FOREIGN KEY (contact_id) REFERENCES Contacts(id),
    FOREIGN KEY (company_id) REFERENCES Companies(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Activities (
    id TEXT PRIMARY KEY,
    contact_id TEXT,
    opportunity_id TEXT,
    type TEXT,
    subject TEXT,
    timestamp TEXT,
    duration_minutes INTEGER,
    outcome TEXT,
    notes TEXT,
    FOREIGN KEY (contact_id) REFERENCES Contacts(id),
    FOREIGN KEY (opportunity_id) REFERENCES Opportunities(id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()