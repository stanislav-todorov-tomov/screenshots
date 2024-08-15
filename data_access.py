from glob import glob
from os.path import join, isdir, isfile
from typing import List

from psycopg import Connection, connect, Cursor
from psycopg.sql import SQL, Identifier

from config import Configuration


class FileSystemAccess:

    def __init__(self):
        self._base_dir = Configuration.base_dir()

    def get_files(self, dir_name: str) -> List[str]:
        dir_path: str = join(self._base_dir, dir_name)
        if isdir(dir_path):
            return [f.replace('\\', '/') for f in glob(f'{dir_path}/*.png') if isfile(f)]
        else:
            return []


class DatabaseAccess:

    def __init__(self):
        self._conn: Connection = connect(Configuration.connection_string())

    def close(self):
        self._conn.close()

    def add_item(self, item_name: str) -> str:
        query = SQL("INSERT INTO {tbl} ({col}) VALUES ({item})").format(
            tbl=Identifier('screenshots'),
            col=Identifier('name'),
            item=item_name)
        cursor: Cursor = self._conn.cursor()
        cursor.execute(query)
        self._conn.commit()
        item_id: str = self.get_run_name(item_name)
        cursor.close()
        return item_id

    def execute_select(self, query) -> str:
        cursor: Cursor = self._conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result: str = rows[0][0]
            cursor.close()
            return str(result)
        else:
            cursor.close()
            raise ValueError(f'Item not found.')

    def get_item_name(self, item_id: int) -> str:
        query = SQL("SELECT {name_col} FROM {tbl} WHERE {id_col} = {id_value}").format(
            tbl=Identifier('screenshots'),
            name_col=Identifier('name'),
            id_col=Identifier('id'),
            id_value=item_id)
        return self.execute_select(query)

    def get_run_name(self, run_id: str) -> str:
        query = SQL("SELECT {name_col} FROM {tbl} WHERE {id_col} = {run_name}").format(
            tbl=Identifier('screenshots'),
            name_col=Identifier('name'),
            id_col=Identifier('id'),
            run_name=run_id)
        return self.execute_select(query)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DataAccess:

    def __init__(self):
        self._filesystem = FileSystemAccess()
        self._database = DatabaseAccess()

    def get_files_by_id(self, run_id: str) -> List[str]:
        run_name: str = self._database.get_item_name(int(run_id))
        return self._filesystem.get_files(run_name)

    def add_run(self, run_name: str) -> str:
        return self._database.add_item(run_name)
