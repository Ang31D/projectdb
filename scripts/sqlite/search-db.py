from Script import Script
import core.sqlite_helper as db
import csv
import os
from tabulate import tabulate
from itertools import repeat

"""
search database

--script search-db --script-args db=<file.db> table=<table_name>
"""

class init(Script):
	def __init__(self):
		super().__init__()
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Search database"
		self.requirements.append("sqlite")
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("sqlite")

	def _on_help(self):
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		help_output = "  This script is used for searching through connected and attached database(s)."
		help_output += "\n%s" % "  Use '--script-args' to pass options to the script."
		#help_output += "\n\n%s" % "  * Options (required):"
		help_output += "\n"

		"""
			'main' options; used for finding 'stuff'
		"""
		help_output += "\n%s" % "  * Options (optional):"
		help_output += "\n%s" % "    find='<value>'          - value to search for; if omitted, match on any with look-for 'db', 'table' or 'column'"
		help_output += "\n%s" % "    look-for='<type>'       - what to find; valid types: 'db', 'table', 'column', 'field' (default)"
		help_output += "\n%s" % "    table='<table_name>'    - the table to search in"
		help_output += "\n%s" % "    column='<column_name>'  - the column to match on; comma separated list"
		help_output += "\n%s" % "    db-name='<db_name>'     - overrides default (\"main\") db which the table exists in"
		help_output += "\n"
		"""
			'match' options; conditionalizes the 'find' match
		"""
		help_output += "\n%s" % "    * Match"
		help_output += "\n%s" % "      match='<option>'      # comma separated list of options; available options:"
		help_output += "\n%s" % "        multi               - match on multiple 'find' values; values separated by '|'"
		help_output += "\n%s" % "        reverse             - negative match on 'find' value"
		help_output += "\n"
		"""
			'format' options; controls the output
		"""
		help_output += "\n%s" % "    * Output Format"
		help_output += "\n%s" % "      format='<option>'     # one option only; available options:"
		help_output += "\n%s" % "        no-columns          - skip output of columns"
		help_output += "\n%s" % "        wrap                - as 'no-columns' but does also wrap the output; replace char '\\n' with '\\n\\t'"
		help_output += "\n"
		"""
			'extra' options;  to control the output
		"""
		help_output += "\n%s" % "    * Extra options"
		help_output += "\n%s" % "      options='<option>'    # comma separated list of options; available options:"
		help_output += "\n%s" % "        exclude-sysdbs      - exclude system tables during search"
		help_output += "\n%s" % "        full-width          - does not strip field value when more then 100 in length"
		help_output += "\n\n"
		help_output += "\n%s" % " * Examples"
		help_output += "\n%s" % "   --script search-db --script-args db=db/csrid.db options='exclude-sysdbs,full-width'"
		help_output += "\n"
		help_output += "\n%s" % "   Search on multi value match"
		help_output += "\n%s" % "   %s" % ("-"*len("Search on multiple value match"))
		help_output += "\n%s" % "   find records in 'hash_map' table that match on either 'gitee' or 'hybrid' in the 'comment' column"
		help_output += "\n%s" % "   --script-args table=hash_map column=comment find='gitee|hybrid' match=multi"
		help_output += "\n"
		help_output += "\n%s" % "   find records in 'hash_map' table that does not match on 'jsonl' and 'virustotal' in the 'comment' column"
		help_output += "\n%s" % "   --script-args table=hash_map column=comment find='jsonl|virustotal' match=multi,reverse"
		return help_output
	
	def _on_run(self, args):
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
		db_name = None
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
			db_name = table[0]
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

		# // script options
		# ----------------------------------------------------------------
		out_full_width = False
		tablefmt='github'
		if "options" in args:
			option_args = args["options"]["value"].split(",")
			out_full_width = "full-width" in option_args
		
		out_format = None
		if "format" in args:
			out_format = args["format"]["value"]
		# ----------------------------------------------------------------

		table_list = []
		for table in tables:
			db_name = table[0]
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

		headers = ['db', 'table', 'column', 'value']
		self._output_table(table_list, headers, out_format)

	def _search_db_for_record_in_table(self, db_conn, db_name, table_name, find_value, args):
		tables = db.tables(db_conn, db_name, None)

		# // script options
		# ----------------------------------------------------------------
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

		out_format = None
		if "format" in args:
			out_format = args["format"]["value"]
		# ----------------------------------------------------------------

		#headers = ['db', 'table', 'column', 'value']
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

		self._output_table(table_list, headers, out_format)

	def _output_table(self, table_list, headers, out_format=None):
		tablefmt='github'
		wrap_data = False

		if out_format is not None:
			if out_format == "no-columns" or out_format == "wrap":
				tablefmt='plain'
				headers = []
			if out_format == "wrap":
				wrap_data = True
		
		out_data = tabulate(table_list, headers=headers, tablefmt=tablefmt)

		if wrap_data:
			print(out_data.replace("\\n", "\n\t"))
		else:
			print(out_data)