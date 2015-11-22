#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('DB/test.db')
print "Opened database successfully";

conn.execute('pragma foreign_keys=ON')
conn.execute('''CREATE TABLE USERS
       (ID INTEGER PRIMARY KEY,
       NAME           TEXT  UNIQUE  NOT NULL);''')

conn.execute('''CREATE TABLE CASES
            (ID INTEGER PRIMARY KEY,
            NAME           TEXT  UNIQUE  NOT NULL,
            DESCRIPTION    TEXT     NOT NULL,
            FILTERID       INT,
            FOREIGN KEY (FILTERID) REFERENCES FILTERS(ID));''')

conn.execute('''CREATE TABLE FILES
            (ID INTEGER PRIMARY KEY,
            FILENAME       TEXT    NOT NULL,
            TYPE           TEXT    NOT NULL,
            CASEID         INT,
            FILTERID       INT,
            SIZE           INT,
            FIRST_PACKET_DATETIME TEXT,
            LAST_PACKET_DATETIME TEXT,
            SOURCE_FILE TEXT,
            FOREIGN KEY (FILTERID) REFERENCES FILTERS(ID),
            FOREIGN KEY (CASEID) REFERENCES CASES(ID));''')

conn.execute('''CREATE TABLE FILTERS
            (ID INTEGER PRIMARY KEY,
            CONTENT         TEXT    NOT NULL);''')

conn.execute('''CREATE TABLE USERCASE
            (USERID INT,
            CASEID  INT,
            FOREIGN KEY(USERID) REFERENCES USERS(ID),
            FOREIGN KEY(CASEID) REFERENCES CASES(ID));''')
print "Tables created successfully";
conn.commit()
conn.close()
