import core.sqlite_helper as db
import csv
import os
from tabulate import tabulate
from itertools import repeat

"""
search database

--script search-db --script-args db=<file.db> table=<table_name>
"""

class script:
	def __init__(self):
		self.name = '.'.join(os.path.basename(__file__).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Search database"
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
		detailed_output  = "\n  Search database"
		detailed_output += "\n  Use '--script-args' to pass options to this script."
		detailed_output += "\n\n  * Options (required):"
		#detailed_output += "\n    db='<file.db>'          - the database (.db) file to connect to"
		detailed_output += "\n"
		detailed_output += "\n  * Options (optional):"
		detailed_output += "\n    find='<value>'          - value to search for; if omitted match on any with look-for: 'db', 'table' or 'column'"
		detailed_output += "\n    look-for='<type>'       - what to find; valid types: 'db', 'table', 'column', 'field' (default)"
		detailed_output += "\n    table='<table_name>'    - the table to search in"
		detailed_output += "\n    column='<column_name>'  - the column to match on; comma separated list"
		#detailed_output += "\n    match='reverse'         - negative match on 'find' value"
		#detailed_output += "\n    match='multi'           - match on multiple values; separated 'find' values by '|'"
		#detailed_output += "\n    exclude='sysdbs'        - exclude sysdbs during search"
		detailed_output += "\n    db-name='<db_name>'     - overrides default (\"main\") db which the table exists in"
		#detailed_output += "\n    out='full-width'        - does not strip field value when more then 100 in length"
		detailed_output += "\n"
		detailed_output += "\n    * Match options"
		detailed_output += "\n      match='<option>'      # comma separated list of options; available options:"
		detailed_output += "\n        multi       - match on multiple 'find' values; values separated by '|'"
		detailed_output += "\n        reverse     - negative match on 'find' value"
		detailed_output += "\n"
		detailed_output += "\n    * Extra options"
		detailed_output += "\n      options='<option>'    # comma separated list of options; available options:"
		detailed_output += "\n        exclude-sysdbs   - exclude system tables during search"
		detailed_output += "\n        full-width       - does not strip field value when more then 100 in length"
		detailed_output += "\n\n"
		detailed_output += "\n * Examples"
		detailed_output += "\n   --script search-db --script-args db=db/csrid.db options='exclude-sysdbs,full-width'"
		detailed_output += "\n"
		detailed_output += "\n   Search on multi value match"
		detailed_output += "\n   %s" % ("-"*len("Search on multiple value match"))
		detailed_output += "\n   find records in 'hash_map' table that match on either 'gitee' or 'hybrid' in the 'comment' column"
		detailed_output += "\n   --script-args table=hash_map column=comment find='gitee|hybrid' match=multi"
		detailed_output += "\n"
		detailed_output += "\n   find records in 'hash_map' table that does not match on 'jsonl' and 'virustotal' in the 'comment' column"
		detailed_output += "\n   --script-args table=hash_map column=comment find='jsonl|virustotal' match=multi,reverse"


		print(detailed_output)

	def run(self, args={}):
		if "sqlite.db_conn" not in self._extend:
			print("[!] error: %s; missing 'sqlite.db_conn' extention" % self.name)
			return

		# // check requirements
		#if 'db' not in args:
		#	print("[!] error: %s; required 'db' option missing" % self.name)
		#	return

		self._search_db(args)

	def _connect_db(self, db_file):
		if not db.db_exists(db_file):
			print("[!] error: %s; database failed to connect - missing file '%s'" % (self.name, db_file))
			return None
		db_conn = db.connect(db_file)
		if db_conn is None:
			print("[!] error: %s; database failed to connect - '%s'" % (self.name, db_file))
			return None
		return db_conn

	def _search_db_for_db_name(self, db_conn, find_db_name, exclude_sysdbs):
		db_list = db.databases(db_conn)

		table_list = []
		for i in range(len(db_list)):
			# convert tuple to list
			db_list[i] = [*db_list[i],]
			db_list[i] = db_list[i][:-1] # remove path to db file
			db_list[i] = db_list[i][1:] # remove seq to db file
			db_name = db_list[i][0]

			if find_db_name is not None:
				if find_db_name.lower() not in db_name.lower():
					continue
			table_list.append(db_list[i])

		headers = ['db']
		print(tabulate(table_list, headers=headers, tablefmt='github'))

	def _search_db_for_table(self, db_conn, db_name, find_table_name, exclude_sysdbs):
		tables = db.tables(db_conn, db_name, None)

		table_list = []
		for table in tables:
			table_name = table[1]
			if table_name in db.SYSDBS:
				if exclude_sysdbs:
					continue
			if find_table_name is not None:
				if find_table_name.lower() not in table_name.lower():
					continue
			table_list.append(table)
	
		headers = ['db', 'table']
		table_list = list(map(lambda n: n[0:2], table_list))
		print(tabulate(table_list, headers=headers, tablefmt='github'))

	def _search_db_for_column(self, db_conn, db_name, find_column_name, exclude_sysdbs, args):
		tables = db.tables(db_conn, db_name, None)

		reverse_match = False
		multi_match = False
		if "match" in args:
			match_args = args["match"]["value"].split(",")
			reverse_match = "reverse" in match_args
			multi_match = "multi" in match_args
		
		match_found = False
		table_list = []
		for table in tables:
			table_name = table[1]
			if table_name in db.SYSDBS:
				if exclude_sysdbs:
					continue
			columns = db.columns(db_conn, db_name, table_name)
			for i in range(len(columns)):
				match_found = False
				# convert tuple to list
				columns[i] = [*columns[i],]
				column_name = columns[i][1]

				if find_column_name is not None:
					if multi_match:
						for field_name in find_column_name.split("|"):
							if field_name.lower() in column_name.lower():
								match_found = True
								#table_list.append([db_name, table_name, column_name])
								break
					else:
						if find_column_name.lower() in column_name.lower():
							match_found = True
							#table_list.append([db_name, table_name, column_name])
				else:
					match_found = True


					#if find_column_name.lower() not in column_name.lower():
					#	continue
				if match_found:
					if not reverse_match:
						#table_list.append(row_list)
						table_list.append([db_name, table_name, column_name])
				elif reverse_match:
					#table_list.append(row_list)
					table_list.append([db_name, table_name, column_name])

				# prefix column_info with db & table name
				#table_list.append([db_name, table_name, column_name])
	
		headers = ['db', 'table', 'column']
		print(tabulate(table_list, headers=headers, tablefmt='github'))

	def _search_db_for_record_field(self, db_conn, db_name, find_value, exclude_sysdbs, args):
		tables = db.tables(db_conn, db_name, None)

		if find_value is None:
			print("[!] error: %s; missing 'find' option" % self.name)
			return

		#out_full_width = False
		#if "out" in args and "full-width" == args["out"]["value"]:
		#	out_full_width = True
		out_full_width = False
		if "options" in args:
			option_args = args["options"]["value"].split(",")
			out_full_width = "full-width" in option_args

		headers = ['db', 'table', 'column', 'value']
		table_list = []
		for table in tables:
			table_name = table[1]
			if table_name in db.SYSDBS and exclude_sysdbs:
				continue

			table_columns = db.table_columns(db_conn, db_name, table_name)

			query = '''
				SELECT * FROM %s
			''' % table_name
			rows = db.query_db(db_conn, query)
			for row in rows:
				# convert tuple to list
				row = [*row,]
				for i in range(len(table_columns)):
					column_name = table_columns[i]
					column_value = row[i]
					if find_value is not None:
						if find_value.lower() not in str(column_value).lower():
							continue
					column_value = column_value.rstrip()
					if not out_full_width and len(column_value) > 100:
						column_value = "%s...<STRIPPED>" % column_value[:100]
					table_list.append([db_name, table_name, column_name, column_value])

		print(tabulate(table_list, headers=headers, tablefmt='github'))

	def _search_db_for_record_in_table(self, db_conn, db_name, table_name, find_value, args):
		tables = db.tables(db_conn, db_name, None)

		#out_full_width = False
		#if "out" in args and "full-width" == args["out"]["value"]:
		#	out_full_width = True
		out_full_width = False
		if "options" in args:
			option_args = args["options"]["value"].split(",")
			out_full_width = "full-width" in option_args

		field_name = None
		if "column" in args:
			field_name = args["column"]["value"]

		reverse_match = False
		multi_match = False
		if "match" in args:
			match_args = args["match"]["value"].split(",")
			reverse_match = "reverse" in match_args
			multi_match = "multi" in match_args

		headers = ['db', 'table', 'column', 'value']
		table_list = []
		if not db.table_exists_in_db(db_conn, db_name, table_name):
			print("[!] warning: %s; table not found - '%s'" % (self.name, table_name))
			return

		table_columns = db.table_columns(db_conn, db_name, table_name)
		headers = table_columns

		query = '''
			SELECT * FROM %s
		''' % table_name
		rows = db.query_db(db_conn, query)
		for row in rows:
			# convert tuple to list
			row = [*row,]

			row_list = []
			match_found = False
			for i in range(len(row)):
				field_value = row[i]
				column_name = table_columns[i]

				mod_column_value = field_value.rstrip()
				if not out_full_width and len(field_value) > 100:
					mod_column_value = "%s...<STRIPPED>" % field_value[:100]
				row_list.append(mod_column_value)

				if not multi_match:
					if field_name is not None:
						if field_name.lower() != column_name.lower():
							continue
					if find_value.lower() in str(field_value).lower():
						match_found = True
				else:
					if field_name is not None:
						if field_name.lower() != column_name.lower():
							continue
					find_values = find_value.split("|")
					for match_on_value in find_values:
						if match_on_value.lower() in str(field_value).lower():
							match_found = True
							break
			
			if match_found:
				if not reverse_match:
					table_list.append(row_list)
			elif reverse_match:
				table_list.append(row_list)

		print(tabulate(table_list, headers=headers, tablefmt='github'))

	def _search_db(self, args):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		search_value = None
		if "find" in args:
			search_value = args["find"]["value"]

		#exclude_sysdbs = False
		#if "exclude" in args and "sysdbs" == args["exclude"]["value"]:
		#	exclude_sysdbs = True
		exclude_sysdbs = False
		if "options" in args:
			option_args = args["options"]["value"].split(",")
			exclude_sysdbs = "exclude-sysdbs" in option_args

		db_name = "main" # default database
		if 'db-name' in args:
			db_name = args['db-name']['value']
		
		search_table = None
		if 'table' in args:
			search_table = args['table']['value']

		look_for = "field"
		if "look-for" in args:
			look_for = args["look-for"]["value"]

		#db_file = args['db']['value']
		#db_conn = self._connect_db(db_file)
		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return


		if   "db" == look_for:
			self._search_db_for_db_name(db_conn, search_value, exclude_sysdbs)
		elif "table" == look_for:
			self._search_db_for_table(db_conn, db_name, search_value, exclude_sysdbs)
		elif "column" == look_for:
			self._search_db_for_column(db_conn, db_name, search_value, exclude_sysdbs, args)
		elif "field" == look_for:
			if search_value is None:
				print("[!] error: %s; required 'find' option missing during '%s' look-up" % (self.name, look_for))
				return
			if search_table is None:
				self._search_db_for_record_field(db_conn, db_name, search_value, exclude_sysdbs, args)
			else:
				self._search_db_for_record_in_table(db_conn, db_name, search_table, search_value, args)
		else:
			print("[!] warning: %s; look-for type not supported - '%s'" % (self.name, look_for))

		db.close(db_conn)