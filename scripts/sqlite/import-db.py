from Script import Script
import core.sqlite_helper as db
import csv
import os
from tabulate import tabulate
from itertools import repeat

class init(Script):
	def __init__(self):
		super().__init__()
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Import database records"
		self.requirements.append("sqlite")
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("sqlite")

	def _on_help(self):
		help_output  = "\n  Imports csv-data as records into the database table"
		help_output += "\n  Use '--script-args' to pass options to this script."
		help_output += "\n"
		help_output += "\n  * Options:"
		help_output += "\n    table='<table_name>'  - the table name to import into"
		help_output += "\n    file='<file.csv>'     - the file containing (csv) data to import from"
		help_output += "\n"
		help_output += "\n    db-name='<db_name>'   - (optional) overrides default (\"main\") db which the table exists in"
		return help_output

	def _on_run(self, args):
		if 'table' not in args:
			print("[!] error: %s; missing 'table' option" % self.name)
			return
		if 'file' not in args:
			print("[!] error: %s; missing 'file' option" % self.name)
			return

		self._import_db(args)

	def _import_db(self, args):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		table_name = args['table']['value']
		data_file = args['file']['value']

		db_name = 'main'
		if 'db-name' in args:
			db_name = args['db-name']['value']

		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return

		if not db.table_exists(db_conn, table_name):
			print("[!] error: %s; missing table - '%s'" % (self.name, table_name))
			db.close(db_conn)
			return
	
		column_list = db.table_columns(db_conn, db_name, table_name)
		table_columns = ', '.join(column_list)
		query_values = ', '.join(list(repeat("?", len(column_list))))
	
		query_param = """INSERT INTO %s
					(%s) 
					VALUES (%s);""" % (table_name, table_columns, query_values)

		cur = db_conn.cursor()
		with open(data_file) as f:
			csv_reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			cur.executemany(query_param, csv_reader)
			db_conn.commit()

			print("[*] table '%s' imported <- '%s'" % (table_name, data_file))
	
		db.close(db_conn)