# The purpose of smugler is to read varius http headers from incoming requests
# and store them in a database for later analysis.
# Some of the headers are:
#   - X-File-Name (defalt to file)
#   - X-File-Extension (default to txt)
#   - X-Payload
# 
# The database is a sqlite3 database and the table is called smugler.
# The table has the following columns:
#   - id (autoincrement)
#   - timestamp (timestamp of the request)
#   - filename (filename of the request)
#   - extension (extension of the request)
#   - payload (payload of the request)
#
# Some COC:
#   - String concatenation is done with the f-string method
# example: f"CREATE TABLE IF NOT EXISTS {DbTable} (id INTEGER PRIMARY KEY, timestamp TEXT, filename TEXT, extension TEXT, payload TEXT)"

from bottle import request, response, route, run
#import bottle
import sqlite3
import os
import sys
import time
import datetime
import argparse
import logging

# Global variables
DbFile = "smugler.db"
DbTable = "smugler"
DbTableCreate = f"CREATE TABLE IF NOT EXISTS {DbTable} (id INTEGER PRIMARY KEY, timestamp TEXT, filename TEXT, extension TEXT, payload TEXT)"
DbTableInsert = "INSERT INTO " + DbTable + " (timestamp, filename, extension, payload) VALUES (?, ?, ?, ?)"

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def initiate_database():
    # Check if database exists
    if not os.path.isfile(DbFile):
        # Create database
        logging.info(f"Creating database {DbFile}")
        conn = sqlite3.connect(DbFile)
        c = conn.cursor()
        c.execute(DbTableCreate)
        conn.commit()
        conn.close()
    else:
        logging.info(f"Database {DbFile} already exists")


@route('/', method=['GET', 'POST'])
def index():
    # Get headers
    headers = request.headers
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    filename = headers.get('X-File-Name', '')
    extension = headers.get('X-File-Extension', '')
    payload = headers.get('X-Payload', '')

    # Insert into database
    conn = sqlite3.connect(DbFile)
    c = conn.cursor()
    c.execute(DbTableInsert, (timestamp, filename, extension, payload))
    conn.commit()
    conn.close()

    return "OK"


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description='Smugler')
    parser.add_argument('--host', dest='host', help='Host to listen to', default='0.0.0.0')
    parser.add_argument('--port', dest='port', help='Port to listen to', default=8080)
    args = parser.parse_args()

    # Initiate database
    initiate_database()
    
    # Start server
    logging.info(f"Starting server on {args.host}:{args.port}")
    run(host=args.host, port=args.port, reloader=True)

