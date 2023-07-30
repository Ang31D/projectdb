import core.sqlite_helper as db
import csv
import os
from tabulate import tabulate
from itertools import repeat

"""
import database records

--script import-records --script-args db=<file.db> file=<data.csv> table=<table_name>
"""

class init:
	def __init__(self):
		self.name = '.'.join(os.path.basename(__file__).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Import database records"
		self.requirements = ["sqlite"]
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories = ["sqlite"]
		self._extend = {}
		self._set_categories()
		self._script_repo_dir = None

	@property
	def categories(self):
		return self._categories

	def extend(self, data={}):
		key_list = list(data.keys())
		if len(key_list) == 0:
			return
		for key in key_list:
			self._extend[key] = data[key]

	def _set_categories(self):
		parent_dir_path = os.path.dirname(os.path.realpath(__file__))
		parent_dir_name = os.path.basename(os.path.realpath(parent_dir_path))
		if parent_dir_name == "scripts":
			self._categories.append("generic")
		else:
			if "/scripts/" in parent_dir_path:
				dir_index = parent_dir_path.rindex("/scripts/")
				scripts_root_dir = parent_dir_path[dir_index+1:]
				dir_names = scripts_root_dir.split("/")[1:]
				for dir_name in dir_names:
					if dir_name not in self._categories:
						self._categories.append(dir_name)
			elif parent_dir_name not in self._categories:
				self._categories.append(parent_dir_name)

	def _script_internals(self):
		data = ""
		if "_internal.script" in self._extend:
			data = "[INTERNALS]"
			int_table = []
			for key in self._extend["_internal.script"]:
				int_table.append(["  ", "%s" % key, ":", "%s" % self._extend["_internal.script"][key]])
			
			data += "\n%s" % tabulate(int_table, tablefmt='plain')
			if "_internal.script.args" in self._extend:
				script_args = self._extend["_internal.script.args"]
				if self.name in script_args and "args" in script_args[self.name]:
					args = script_args[self.name]["args"]
					data += "\n\n  * Options"
					if len(list(args)) > 0:
						int_table = []
						for key in args:
							int_table.append(["  ", "%s" % key, ":", "%s" % args[key]["value"]])
						data += "\n%s" % tabulate(int_table, tablefmt='plain')
				else:
					data += "\n%s" % script_args
		else:
			data += "\n%s" % "[!] error: extention not found - '%s'" % "_internal.script"
		return data
	def help(self):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		output = self.name
		output += "\nCategories: %s" % ' '.join(self.categories)
		output += "\nRequirements: %s" % ' '.join(self.requirements)
		print(output)
		if verbose_mode:
			print("-"*88)
			print(self._script_internals())
			print("-"*88)
		else:
			print("%s" % __file__)
			pass
		output = "  %s" % self.description
		print(output)
		# max 93 in length until new line (\n)
		# ex.:             "\n --------------------------------------------------------------------------------------------
		detailed_output  = "\n  Imports csv-data as records into the database table"
		detailed_output += "\n  Use '--script-args' to pass options to this script."
		detailed_output += "\n\n  * Options:"
		#detailed_output += "\n    db='<file.db>'        - the database (.db) file to connect to"
		detailed_output += "\n    table='<table_name>'  - the table name to import into"
		detailed_output += "\n    file='<file.csv>'     - the file containing (csv) data to import from"
		detailed_output += "\n\n    db-name='<db_name>'   - (optional) overrides default (\"main\") db which the table exists in"

		print(detailed_output)

	def run(self, args={}):
		if "sqlite.db_conn" not in self._extend:
			print("[!] error: %s; missing 'sqlite.db_conn' extention" % self.name)
			return

		# // check requirements
		#if 'db' not in args:
		#	print("[!] error: %s; missing 'db' option" % self.name)
		#	return
		if 'table' not in args:
			print("[!] error: %s; missing 'table' option" % self.name)
			return
		if 'file' not in args:
			print("[!] error: %s; missing 'file' option" % self.name)
			return

		self._import_db(args)

	def _connect_db(self, db_file):
		if not db.db_exists(db_file):
			print("[!] error: %s; database failed to connect - missing file '%s'" % (self.name, db_file))
			return None
		db_conn = db.connect(db_file)
		if db_conn is None:
			print("[!] error: %s; database failed to connect - '%s'" % (self.name, db_file))
			return None
		return db_conn

	def _import_db(self, args):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		table_name = args['table']['value']
		data_file = args['file']['value']

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
	
		column_list = db.table_columns(db_conn, db_name, table_name)
		table_columns = ', '.join(column_list)
		quest_values = ', '.join(list(repeat("?", len(column_list))))
	
		query_param = """INSERT INTO %s
					(%s) 
					VALUES (%s);""" % (table_name, table_columns, quest_values)

		cur = db_conn.cursor()
		with open(data_file) as f:
			csv_reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			cur.executemany(query_param, csv_reader)
			db_conn.commit()

			print("[*] table '%s' imported <- '%s'" % (table_name, data_file))
	
		db.close(db_conn)