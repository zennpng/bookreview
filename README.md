## Simple Book Review Website using Flask and SQL

Run Flask using 'Flask run'
- app.py will be run automatically by Flask server 
- if error occurs, manually set DATABASE_URL environment variable before running server
Database: PostgreSQL hosted by Heroku,
Additional Data Resource: Goodreads via API
- Set up: https://www.goodreads.com/api/keys 
- Implementations: https://www.goodreads.com/api
Use import.py to set up postgresql database tables and push books.csv there,
Templates contain website's HTML files,
Update credentials in credentials.py,
pip install -r requirements.txt,
Website own API: "/api/<isbn>" route
