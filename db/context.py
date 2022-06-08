#!/usr/bin/env python3
from datetime import datetime, timedelta
import sqlite3
import time
from typing import List, Tuple


class DataContext:

    def __init__(self, path: str) -> None:
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
        cur.execute('''CREATE TABLE error_measurements (filename, time);''')
        cur.execute('''CREATE TABLE processed_files (filename);''')
        cur.execute('''INSERT INTO migrations VALUES (1)''')
        self.ctx.commit()

    def insertMeasurements(self, filename: str, measurements: List[tuple[datetime, int, int]], error_measurements: List[datetime]) -> None:
        cur = self.ctx.cursor()
        cur.executemany('''INSERT INTO measurements VALUES (?,?,?,?);''', list(map(lambda x: (filename,)+x, measurements)))
        cur.executemany('''INSERT INTO error_measurements VALUES (?,?);''', list(map(lambda x: (filename,x,), error_measurements)))
        cur.execute('''INSERT INTO processed_files VALUES (?);''', (filename,))
        self.ctx.commit()

    def getProcessedFiles(self) -> List[str]:
        cur = self.ctx.cursor()
        cur.execute('''SELECT filename FROM processed_files;''')
        return [filename for (filename, ) in cur.fetchall()]

    def clearFile(self, filename: str) -> None:
        cur = self.ctx.cursor()
        cur.execute('''DELETE FROM error_measurements WHERE filename = :filename;''', {"filename": filename})
        cur.execute('''DELETE FROM measurements WHERE filename = :filename;''', {"filename": filename})
        cur.execute('''DELETE FROM processed_files WHERE filename = :filename;''', {"filename": filename})
        self.ctx.commit()

    def get_days(self) -> List[str]:
        cur = self.ctx.cursor()
        cur.execute('''SELECT filename FROM processed_files;''')
        days = []
        for (filename, ) in cur.fetchall():
            day = datetime.strftime(datetime.strptime(filename, '%Y-%m-%d_%H-%M-%S.mp4'), "%Y-%m-%d")
            if day not in days:
                days.append(day)
        return days

    def get_measurements_for_day(self, day):
        cur = self.ctx.cursor()
        cur.execute('''SELECT substr(time,1,19), AVG(k1), AVG(k2) FROM measurements m WHERE filename LIKE :day GROUP BY 1;''', {"day": day+"%"})
        return cur.fetchall()
