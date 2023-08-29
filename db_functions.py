import sqlite3
import pandas as pd


# Функция создания таблицы
def create_table(name_BD, name_table, table):
    # создаём движок
    conn = sqlite3.connect(name_BD)
    table.to_sql(name_table, conn, index=False)
    conn.close()


# Функция удаления таблицы из БД
def drop_table(name_BD, name_table):
    conn = sqlite3.connect(name_BD)
    conn.execute(f'DROP TABLE {name_table};')
    conn.commit()  # фиксируем изменение
    conn.close()


# Функция получения таблицы
def get_table(name_BD, name_table):
    # создаём движок
    conn = sqlite3.connect(name_BD)
    table = pd.read_sql(f' SELECT * FROM {name_table}', conn)
    conn.close()

    return table


# Функция получения строки по ндексу
def get_row_by_index(name_BD, name_table, index):
    connection = sqlite3.connect(name_BD)
    table = pd.read_sql(f'''SELECT * FROM {name_table} WHERE rowid = {index + 1} ;''', connection)  # +1 криво
    connection.close()
    return table


# Функция добавления строки в БД
def insert_row(name_BD, name_table, row):
    conn = sqlite3.connect(name_BD)
    conn.execute(f'INSERT INTO {name_table} VALUES {row};')
    conn.commit()  # фиксируем изменение
    conn.close()


def get_rows_by_inter(name_BD, name_table, start_ind, end_ind):
    conn = sqlite3.connect(name_BD)
    table = pd.read_sql(f'''
    SELECT * 
    FROM {name_table} 
    WHERE rowid >= {start_ind + 1} AND rowid < {end_ind + 1};''', conn)  # +1 криво

    conn.close()
    return table
