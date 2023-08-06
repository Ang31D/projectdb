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
		help_output  = "  Delete record from a database table"
		help_output += "\n  Use '--script-args' to pass options to this script."
		help_output += "\n"
		help_output += "\n  * Options:"
		help_output += "\n    table='<table_name>'    - table the record exists in"
		help_output += "\n    column='<column_name>'  - column to match on"
		help_output += "\n    match-on='<value>'      - value to match on"
		help_output += "\n"
		help_output += "\n    db-name='<db_name>'     - overrides default (\"main\") db which the table exists in"
		help_output += "\n    options='dry-mode'      - (optional) do not commit to database, good for verification"
		return help_output

	def _on_run(self, args):
		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return

		if 'table' not in args:
			print("[!] error: %s; missing required 'table' option" % self.name)
			return
		if 'column' not in args:
			print("[!] error: %s; missing required 'column' option" % self.name)
			return
		if 'match-on' not in args:
			print("[!] error: %s; missing required 'match-on' option" % self.name)
			return

		dry_mode = False
		if "options" in args and "dry-mode" in args["options"]["value"].split(","):
			dry_mode = True

		rows = self._select_record(args)
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