#!/usr/bin/python3
import os
import sqlite3

class Exception:
	OperationalError = sqlite3.OperationalError


def is_sys_table(table_name):
	return table_name.lower().startswith("sqlite_")

def table_definition_from_file(file):
	def_data = None
	if not os.path.isfile(file):
		return def_data

	with open(file, "r") as f:
		def_data = ''
		for line in f.readlines():
			def_data += line
	return def_data

def get_table_from_definition(table_definition):
	if not table_definition.startswith("CREATE TABLE ") and "(" in table_definition:
		return None

	table_name = table_definition[0:table_definition.index("(")]
	table_name = table_name.split(" ")[2]
	return table_name
def rename_table_definition(table_definition, new_table_name):
	defined_table_name = get_table_from_definition(table_definition)
	if defined_table_name is None:
		return None

	start_index_of_table_name = table_definition.index("(") - len(defined_table_name)
	prefix_create_table = table_definition[0:start_index_of_table_name]
	column_definition = table_definition[table_definition.index("("):]
	#print(column_definition)
	renamed_table_definition = "%s%s%s" % (prefix_create_table, new_table_name, column_definition)
	#print("'%s'" % renamed_table_definition)
	#print("defined-table_name: '%s', new-table_name: '%s'" % (defined_table_name, new_table_name))
	return renamed_table_definition
def define_db(db_conn, db_definition):
	try:
		cur = db_conn.cursor()
		cur.execute(db_definition)
		db_conn.commit()
		cur.close()
		return True

	except sqlite3.OperationalError:
		return False

def db_exists(db_file):
	return os.path.isfile(db_file)

def create_db(db_file):
	db_conn = None
	if not os.path.isfile(db_file):
		db_conn = sqlite3.connect(db_file)
	if os.path.isfile(db_file):
		return db_conn
	return db_conn

def connect(db_file):
	conn = None
	if os.path.isfile(db_file):
		conn = sqlite3.connect(db_file)
	return conn

#def db_close(db_conn):
def close(db_conn):
	db_conn.close()

def table_exists(db_conn, table_name):
	table_list = table_names(db_conn, None, table_name)
	return table_name in table_list

def table_exists_in_db(db_conn, db_name, table_name):
	result = False
	if db_name is None or table_name is None:
		return result

	query = '''
		SELECT * FROM pragma_table_info
		WHERE arg='%s' AND schema='%s'
	''' % (table_name, db_name)

	try:
		cur = db_conn.cursor()
		cur.execute(query)
		data_list =  cur.fetchall()
		cur.close()
		return True
	except sqlite3.OperationalError:
		print("sqlite3.OperationalError")
		return False

def truncate_table(db_conn, table_name):
	try:
		cur = db_conn.cursor()
		cur.execute("DELETE FROM '%s';" % table_name)
		db_conn.commit()
		return True
	except sqlite3.OperationalError:
		return False

def drop_table(db_conn, table_name):
	try:
		cur = db_conn.cursor()
		cur.execute("DROP TABLE '%s';" % table_name)
		db_conn.commit()
		return True
	except sqlite3.OperationalError:
		return False
def drop_table_from_database(db_conn, db_name, table_name):
	try:
		cur = db_conn.cursor()
		cur.execute("DROP TABLE %s.%s;" % (db_name, table_name))
		db_conn.commit()
		return True
	except sqlite3.OperationalError:
		return False

def query_db(db_conn, query):
	try:
		cur = db_conn.cursor()
		cur.execute(query)
		rows = cur.fetchall()
		return rows
	except sqlite3.OperationalError:
		return None

""" The Schema Table
	https://www.sqlite.org/schematab.html
"""
def db_tables(db_conn):
	query_param = '''
		SELECT name FROM 
			(SELECT * FROM sqlite_schema UNION ALL
			 SELECT * FROM sqlite_temp_schema)
		WHERE type='table'
		ORDER BY name
	'''
	param_data = ()

	rows = execute(db_conn, query_param, param_data, True)
	if rows is None:
		return []
	return rows

""" PRAGMA table_list in SQLite
https://database.guide/pragma-table_list-in-sqlite/
"""
def tables(db_conn, db_name, table_name):
	pragma_param = 'table_list'
	if db_name is not None:
		pragma_param = '%s.%s' % (db_name, pragma_param)
	if table_name is not None:
		pragma_param = '%s(%s)' % (pragma_param, table_name)
	
	query_param = '''
		PRAGMA %s;
	''' % pragma_param
	
	param_data = ()
	rows = execute(db_conn, query_param, param_data, True)

	if rows is None:
		return []
	return rows
def table_names(db_conn, db_name, table_name):
	rows = tables(db_conn, db_name, table_name)
	name_list = []
	for row in rows:
		name_list.append(row[1])
	return name_list

"""
display column information of the table
"""
def columns(db_conn, db_name, table_name):
	if db_name is None or table_name is None:
		return []

	query = '''
		SELECT * FROM pragma_table_info
		WHERE arg='%s' AND schema='%s'
	''' % (table_name, db_name)

	try:
		cur = db_conn.cursor()
		cur.execute(query)
		return cur.fetchall()
	except sqlite3.OperationalError:
		print("sqlite3.OperationalError")
		return []

def column_names(db_conn, table_name):
	#table_columns = columns(db_conn, db_name, table_name)
	tbl_schema_string = table_schema(db_conn, table_name)
	#print(tbl_schema_string)
	if tbl_schema_string is None:
		return []
	
	tbl_schema = []
	for tbl_schema_line in tbl_schema_string.split("\n"):
		tbl_schema.append(tbl_schema_line.strip())
	tbl_schema_string = ''.join(tbl_schema)

	columns_def = tbl_schema_string[tbl_schema_string.index("(")+1:][:-1]
	columns_defs = columns_def.split(",")
	return list(map(lambda c: c.split(" ")[0], columns_def.split(",")))
	print(columns_def)
	#table_name = table_name.split(" ")[2]
	return tbl_schema_string
def table_columns(db_conn, db_name, table_name):
	if db_name is None or table_name is None:
		return []

	query = '''
		SELECT * FROM pragma_table_info
		WHERE arg='%s' AND schema='%s'
	''' % (table_name, db_name)

	try:
		cur = db_conn.cursor()
		cur.execute(query)
		rows =  cur.fetchall()
		cur.close()
		column_list = []
		for row in rows:
			row = [*row,]
			column_list.append(row[1])
		return column_list
	except sqlite3.OperationalError:
		print("sqlite3.OperationalError")
		return []

def database_names(db_conn):
	db_list = databases(db_conn)
	db_list = list(map(lambda n: n[1], db_list))
	return db_list
def db_count(db_conn):
	return len(databases(db_conn))
def databases(db_conn):
	result = []
	rows = query_db(db_conn, 'PRAGMA database_list')
	for row in rows:
		result.append(list(map(lambda n: n, row)))
	return result

def record_count(db_conn, table_name):
	query = '''
		SELECT COUNT(*) FROM %s
	''' % table_name
	
	records = -1
	rows = query_db(db_conn, query)
	if len(rows) == 1:
		records = rows[0][0]
	return records

def table_schema(db_conn, table_name):
	query_param = '''
		SELECT * FROM 
			(SELECT * FROM sqlite_schema UNION ALL
			 SELECT * FROM sqlite_temp_schema)
		WHERE type='table' AND name=?
		ORDER BY name
	'''
	param_data = (table_name,)
	rows = execute(db_conn, query_param, param_data, True)
	if len(rows) == 1:
		return rows[0][4]
	return None

def db_description(db_conn, table_name):
	query = '''
		SELECT * FROM %s
	''' % table_name
	try:
		cur = db_conn.cursor()
		cur.execute(query)
		result = cur.description
		return result
	except sqlite3.OperationalError:
		return None

def attach_db(db_conn, db_name, db_file):
	query_param = "ATTACH DATABASE ? AS ?"
	param_data = (db_file, db_name,)
	return execute(db_conn, query_param, param_data, False)

	try:
		cur = db_conn.cursor()
		cur.execute(query_param, param_data)
	except sqlite3.OperationalError:
		return None

def execute(db_conn, query_param, param_data, return_data):
	result = None
	try:
		cur = db_conn.cursor()
		cur.execute(query_param, param_data)
		if return_data:
			result = cur.fetchall()
		else:
			result = True
		cur.close()
	except sqlite3.OperationalError:
		if return_data:
			result = None
		else:
			result = False
	return result
