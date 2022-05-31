#!/usr/bin/env python3
from datetime import datetime
import sqlite3
from typing import List


class DataContext:

    def __init__(self, path:str) -> None:
        self.ctx = sqlite3.connect(path)
        self.__migrate()

    def __migrate(self) -> None:
        cur = self.ctx.cursor()
        cur.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='migrations';''')
        migrationTableName = cur.fetchone()
        if migrationTableName is None:
            self.__createDatabase()

        dbVersion = self.__getDbVersion()
        # if dbVersion ==1:
        #     print("migrating")
        print("DB-Version is", dbVersion)

    def __getDbVersion(self) -> None:
        cur = self.ctx.cursor()
        cur.execute('''SELECT version FROM migrations;''')
        return cur.fetchone()[0]

    def __createDatabase(self) -> None:
        print("Creating Database")
        cur = self.ctx.cursor()
        cur.execute('''CREATE TABLE migrations (version);''')
        cur.execute('''CREATE TABLE measurements (filename, time, k1, k2);''')
        cur.execute('''CREATE TABLE processed_files (filename);''')
        cur.execute('''INSERT INTO migrations VALUES (1)''')
        self.ctx.commit()

    def insertMeasurements(self, filename: str, measurements: List[tuple[datetime, int, int]]) -> None:
        cur = self.ctx.cursor()
        cur.executemany('''INSERT INTO measurements VALUES (?,?,?,?);''', list(map(lambda x: (filename,)+x, measurements)))
        cur.execute('''INSERT INTO processed_files VALUES (?);''', (filename,))
        self.ctx.commit()

    def clearFile(self, filename: str) -> None:
        cur = self.ctx.cursor()
        cur.execute('''DELETE FROM measurements WHERE filename = :filename;''', {"filename": filename})
        cur.execute('''DELETE FROM processed_files WHERE filename = :filename;''', {"filename": filename})
        self.ctx.commit()
