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
		self.description = "Delete database record(s)"
		self.requirements.append("sqlite")
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("sqlite")

	def _on_help(self):
		help_output  = "\n  Delete record from a database table"
		help_output += "\n  Use '--script-args' to pass options to this script."
		help_output += "\n"
		help_output += "\n  * Options:"
		help_output += "\n    table='<table_name>'    - table the record exists in"
		help_output += "\n    column='<column_name>'  - column to match on"
		help_output += "\n    match-on='<value>'      - value to match on"
		help_output += "\n    db-name='<db_name>'     - overrides default (\"main\") db which the table exists in"
		help_output += "\n    options='dry-mode'      - (optional) do not commit to database, good for verification"
		return help_output

	def _on_run(self, args):
		if 'table' not in args:
			print("[!] error: %s; missing 'table' option" % self.name)
			return
		if 'column' not in args:
			print("[!] error: %s; missing 'column' option" % self.name)
			return
		if 'match-on' not in args:
			print("[!] error: %s; missing 'match-on' option" % self.name)
			return

		dry_mode = False
		if "options" in args and "dry-mode" in args["options"]["value"].split(","):
			dry_mode = True

		rows = self._select_record(args)
		#self._show_record(rows)
		if rows is None:
			print("Query failed")
			return
		if len(rows) == 0:
			print("no records found")
			return
		
		for row in rows:
			print(row)

		if dry_mode:
			print("[!] dry-mode - no records removed")
			return

		self._del_record(args)

	def _connect_db(self, db_file):
		if not db.db_exists(db_file):
			print("[!] error: %s; database failed to connect - missing file '%s'" % (self.name, db_file))
			return None
		db_conn = db.connect(db_file)
		if db_conn is None:
			print("[!] error: %s; database failed to connect - '%s'" % (self.name, db_file))
			return None
		return db_conn

	def _del_record(self, args):
		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return
		
		query = self._build_delete_query(args)
		#return

		try:
			cur = db_conn.cursor()
			cur.execute(query, ())
			db_conn.commit()
			return True
		except db.Exception.OperationalError:
			return False
	
	def _select_record(self, args):
		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return None

		query = self._build_select_query(args)
		try:
			rows = db.query_db(db_conn, query)
			return rows
		except db.Exception.OperationalError:
			return []
	def _build_select_query(self, args):
		table = args["table"]["value"]
		column = args["column"]["value"]
		match_on = args["match-on"]["value"]

		query = '''SELECT * FROM %s WHERE %s = "%s"
		''' % (table, column, match_on)
		return query
	def _build_delete_query(self, args):
		table = args["table"]["value"]
		column = args["column"]["value"]
		match_on = args["match-on"]["value"]

		query = '''DELETE FROM %s WHERE %s = "%s"
		''' % (table, column, match_on)
		return query

	def _show_record(self, rows):
		for row in rows:
			print(row)

	def _drop_table(self, args):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		table_name = args['table']['value']

		#db_name = None
		db_name = "main" # default database
		if 'db-name' in args:
			db_name = args['db-name']['value']

		dry_mode = False
		if 'mode' in args and "dry" == args['mode']['value']:
			dry_mode = True

		#db_file = args['db']['value']
		#db_conn = self._connect_db(db_file)
		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return
	
		if dry_mode:
			out_drop_statement = "'%s'" % table_name
			if db_name is not None:
				out_drop_statement = "'%s' from db('%s')" % (table_name, db_name)
			print("[*] %s; drop table %s" % (self.name, out_drop_statement))
			if not db.table_exists_in_db(db_conn, db_name, table_name):
				print("[!] %s; dry mode warning: table not found - '%s'" % (self.name, table_name))
			else:
				print("[!] %s; dry mode - would have dropped %s" % (self.name, out_drop_statement))
			db.close(db_conn)
			return

		if db_name is not None:
			if not db.drop_table_from_database(db_conn, db_name, table_name):
				print("[!] error: %s; db_drop_table_from_database(): status: failed - '%s.%s'" % (self.name, db_name, table_name))
				return
			print("[*] table dropped - '%s' from db('%s')" % (table_name, db_name))
		else:
			if not db.drop_table(db_conn, table_name):
				print("[!] error: %s; status: failed - '%s'" % (self.name, table_name))
			else:
				print("[*] table dropped - '%s'" % table_name)
		db.close(db_conn)