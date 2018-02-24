# libraries for server and local database
import sqlite3

class StorageDB(object):
    def __init__(self, db_filename):
        if (db_filename and db_filename.strip() and db_filename != ''):
            # self.conn = sqlite3.connect(db_filename, timeout=1)
            self.conn = sqlite3.connect(
                db_filename, timeout=1, check_same_thread=False)
            self.cursor = self.conn.cursor()
        else:
            # self.conn = sqlite3.connect('wfm.sqlite', timeout=1)
            self.conn = sqlite3.connect(
                'wfm.sqlite', timeout=1, check_same_thread=False)
            self.cursor = self.conn.cursor()

    def CreateTable(self, table, fields):
        if (table and table.strip() and table != ''):
            sql = []
            cols = []
            sql.append('CREATE TABLE IF NOT EXISTS ' + table + ' (')
            for f, v in fields.items():
                cols.append((str(f) + ' ' + str(v)))

            columns = ",".join(cols)
            columns = columns.strip()
            sql.append(columns)
            sql.append(');')
            sql = "".join(sql)
            self.conn.executescript(sql)

    def DropTable(self, table):
        conn = self.conn
        conn.execute("DROP TABLE IF EXISTS " + table)
        self.Commit()

    def Commit(self):
        conn = self.conn
        conn.commit()

    def Delete(self, table, where):
        query = "DELETE FROM {0} WHERE {1};".format(table, where)
        self.cursor.execute(query)
        self.Commit()

    def Insert(self, table, content):
        fields = []
        value = []
        sql = []
        for f, v in content.items():
            fields.append(str(f))
            value.append(str(v))

        columns = ", ".join(fields)
        values = ", ".join(value)

        sql.append("INSERT INTO " + str(table) + " (")
        sql.append(columns)
        sql.append(") values (")
        sql.append(values)
        sql.append(")")
        query = "".join(sql)
        print(query)
        self.cursor.execute(query)
        self.conn.commit()

        return self.cursor.lastrowid

    def InsertParameterized(self, table, content):
        fields = []
        values = []
        dummy = []
        sql = []
        for f, v in content.items():
            fields.append(str(f))
            dummy.append("?")
            values.append(v)

        # columns ="".join(fields)[:-1]
        columns = ", ".join(fields)
        dummys = ", ".join(dummy)

        sql.append("INSERT INTO " + str(table) + " (")
        sql.append(columns)
        sql.append(") values (")
        sql.append(dummys)
        sql.append(")")
        query = "".join(sql)
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.lastrowid

    def UpdateParameterized(self, table, content, where):

        values = []
        query = []
        sql = []
        query.append("UPDATE " + str(table) + " SET ")
        for f, v in content.items():
            sql.append(str(f) + "= ? ")
            values.append(v)

        sets = ", ".join(sql)
        sets = sets[:-1]
        query.append(sets)
        query.append(" WHERE " + str(where))
        sql_query = "".join(query)

        self.cursor.execute(sql_query, values)
        self.conn.commit()
        return self.cursor.lastrowid

    def FetchAllColumns(self, table):
        self.cursor.execute('PRAGMA table_info(' + str(table) + ')')
        return self.cursor.fetchall()

    def FetchAllRows(self, table):
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM ' + str(table))
        return cur.fetchall()

    def GetResults(self, query):
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute(query)
        return cur.fetchall()

    def IsExist(self, table, column, value):
        # query ="SELECT ?  FROM ?  WHERE ?  = ?", (column,table,column,value,)
        query = "SELECT {0} FROM {1} WHERE {0} = '{2}';".format(
            column, table, value)

        self.cursor.execute(query)
        data = self.cursor.fetchone()
        if data is None:
            return False
        else:
            return True

    def GetValue(self, table, column, where):
        # query ="SELECT ?  FROM ?  WHERE ?  = ?", (column,table,column,value,)
        query = "SELECT {0} FROM {1} WHERE {2};".format(column, table, where)

        self.cursor.execute(query)
        data = self.cursor.fetchone()[0]
        return data
