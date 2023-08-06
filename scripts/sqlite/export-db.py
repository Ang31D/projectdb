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
		self.description = "Export database records"
		self.requirements.append("sqlite")
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("sqlite")

	def _on_help(self):
		help_output  = "  Exports database table records into file as csv"
		help_output += "\n  Use '--script-args' to pass options to this script."
		help_output += "\n"
		help_output += "\n  * Options:"
		help_output += "\n    table='<table_name>'  - the table to export from"
		help_output += "\n    file='<out_file>'     - the file to export to"
		help_output += "\n"
		help_output += "\n    db-name='<db_name>'   - (optional) overrides default (\"main\") db which the table exists in"
		help_output += "\n    export='schema'       - (optional) exports the table schema instead of records"
		return help_output

	def _on_run(self, args):
		if 'table' not in args:
			print("[!] error: %s; missing 'table' option" % self.name)
			return
		if 'file' not in args:
			print("[!] error: %s; missing 'file' option" % self.name)
			return

		self._export_db(args)

	def _connect_db(self, db_file):
		if not db.db_exists(db_file):
			print("[!] error: %s; database failed to connect - missing file '%s'" % (self.name, db_file))
			return None
		db_conn = db.connect(db_file)
		if db_conn is None:
			print("[!] error: %s; database failed to connect - '%s'" % (self.name, db_file))
			return None
		return db_conn

	def _export_db(self, args):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		table_name = args['table']['value']
		out_file = args['file']['value']
		export_schema = False
		if 'export' in args and "schema" == args['export']['value']:
			export_schema = True

		db_name = 'main'
		if 'db-name' in args:
			db_name = args['db-name']['value']

		#db_file = args['db']['value']
		#db_conn = self._connect_db(db_file)
		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return

		if not db.table_exists(db_conn, table_name):
			print("[!] error: %s; missing table - '%s'" % (self.name, table_name))
			db.close(db_conn)
			return
	
		if not export_schema:
			self._export_db_table(db_conn, out_file, db_name, table_name)
		else:
			self._export_db_table_schema(db_conn, out_file, table_name)
	
		db.close(db_conn)

	def _export_db_table(self, db_conn, out_file, db_name, table_name):
		if not db.table_exists_in_db(db_conn, db_name, table_name):
			print("[!] error: %s; table not found - '%s'" % (self.name, table_name))
			return
	
		query_param = '''
			SELECT *
			FROM %s
		''' % table_name
		param_data = ()
		rows = db.execute(db_conn, query_param, param_data, True)
	
		column_list = db.table_columns(db_conn, db_name, table_name)
	
		with open(out_file, 'w', newline='') as f:
			csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for row in rows:
				csv_writer.writerow(row)
		print("[*] table '%s' exported -> '%s'" % (table_name, out_file))

	def _export_db_table_schema(self, db_conn, out_file, table_name):
		table_schema = db.table_schema(db_conn, table_name)
		with open(out_file, 'w') as f:
			f.write(table_schema)
		print("[*] table '%s' schema exported -> '%s'" % (table_name, out_file))