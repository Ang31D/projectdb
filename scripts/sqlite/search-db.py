from Script import Script
import core.sqlite_helper as db
import csv
import os
import json
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
		help_output += "\n%s" % "      match-cond='<option>' # one option only; available options:"
		help_output += "\n%s" % "        contains            - <field> contains <value> (default)"
		help_output += "\n%s" % "        exact               - <field> match on exact <value>"
		help_output += "\n%s" % "        startswith          - <field> starts with <value>"
		help_output += "\n%s" % "        endswith            - <field> ends with <value>"
		help_output += "\n%s" % "        has-value           - <field> is not blank"
		help_output += "\n"

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

		exclude_sysdbs = False
		if "options" in args:
			option_args = args["options"]["value"].split(",")
			exclude_sysdbs = "exclude-sysdbs" in option_args

		#db_name = "main" # default database
		db_name = None
		if 'db-name' in args:
			db_name = args['db-name']['value']
		
		search_table = None
		if 'table' in args:
			search_table = args['table']['value']

		look_for = "field"
		if "look-for" in args:
			look_for = args["look-for"]["value"]

		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return

		if   "db" == look_for:
			self._search_db_for_db_name(db_conn, search_value, exclude_sysdbs, args)
		elif "table" == look_for:
			self._search_db_for_table(db_conn, db_name, search_value, exclude_sysdbs, args)
		elif "column" == look_for:
			self._search_db_for_column(db_conn, db_name, search_table, search_value, exclude_sysdbs, args)
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

	def _search_db_for_db_name(self, db_conn, find_value, exclude_sysdbs, args):
		db_list = db.databases(db_conn)

		# // script options
		# ----------------------------------------------------------------
		match_condition = "contains"
		if "match-cond" in args:
			match_condition = args["match-cond"]["value"]

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

		table_list = []
		for i in range(len(db_list)):
			match_found = False
			# convert tuple to list
			db_list[i] = [*db_list[i],]
			db_list[i] = db_list[i][:-1] # remove path to db file
			db_list[i] = db_list[i][1:] # remove seq to db file
			db_name = db_list[i][0]

			if find_value is not None:
				if multi_match:
					for field_name in find_value.split("|"):
						if self.match_on_condition(field_name, db_name, match_condition):
							match_found = True
							break
				elif self.match_on_condition(find_value, db_name, match_condition):
					match_found = True
			else:
				match_found = True
			
			if match_found:
				if not reverse_match:
					table_list.append([db_name])
			elif reverse_match:
				table_list.append([db_name])

		headers = ['db']
		#print(tabulate(table_list, headers=headers, tablefmt='github'))
		self._output_table(table_list, headers, out_format)

	def _search_db_for_table(self, db_conn, match_db_name, find_value, exclude_sysdbs, args):
		tables = db.tables(db_conn, None, None)

		# // script options
		# ----------------------------------------------------------------
		match_condition = "contains"
		if "match-cond" in args:
			match_condition = args["match-cond"]["value"]

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

		table_list = []
		for table in tables:
			match_found = False
			db_name = table[0]
			table_name = table[1]

			if exclude_sysdbs and db.is_sys_table(table_name):
				continue
			if match_db_name is not None and match_db_name != db_name:
				continue

			if find_value is not None:
				if multi_match:
					for field_name in find_value.split("|"):
						if self.match_on_condition(field_name, table_name, match_condition):
							match_found = True
							break
				elif self.match_on_condition(find_value, table_name, match_condition):
					match_found = True
			else:
				match_found = True

			if match_found:
				if not reverse_match:
					table_list.append([db_name, table_name])
			elif reverse_match:
				table_list.append([db_name, table_name])
	
		headers = ['db', 'table']
		#table_list = list(map(lambda n: n[0:2], table_list))
		#print(tabulate(table_list, headers=headers, tablefmt='github'))
		self._output_table(table_list, headers, out_format)

	def _search_db_for_column(self, db_conn, match_db_name, match_table_name, find_value, exclude_sysdbs, args):
		tables = db.tables(db_conn, None, None)

		# // script options
		# ----------------------------------------------------------------
		match_condition = "contains"
		if "match-cond" in args:
			match_condition = args["match-cond"]["value"]

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
		
		table_list = []
		for table in tables:
			db_name = table[0]
			table_name = table[1]

			if exclude_sysdbs and db.is_sys_table(table_name):
				continue
			if match_db_name is not None and match_db_name != db_name:
				continue
			if match_table_name is not None and match_table_name != table_name:
				continue
			columns = db.columns(db_conn, db_name, table_name)
			for i in range(len(columns)):
				match_found = False
				# convert tuple to list
				columns[i] = [*columns[i],]
				column_name = columns[i][1]

				if find_value is not None:
					if multi_match:
						for field_name in find_value.split("|"):
							if self.match_on_condition(field_name, column_name, match_condition):
								match_found = True
								break
					elif self.match_on_condition(find_value, column_name, match_condition):
						match_found = True
				else:
					match_found = True

				if match_found:
					if not reverse_match:
						table_list.append([db_name, table_name, column_name])
				elif reverse_match:
					#table_list.append(row_list)
					table_list.append([db_name, table_name, column_name])

				# prefix column_info with db & table name
				#table_list.append([db_name, table_name, column_name])
	
		headers = ['db', 'table', 'column']
		#print(tabulate(table_list, headers=headers, tablefmt='github'))
		self._output_table(table_list, headers, out_format)

	def _search_db_for_record_field(self, db_conn, match_db_name, find_value, exclude_sysdbs, args):
		tables = db.tables(db_conn, None, None)

		if find_value is None:
			print("[!] error: %s; missing 'find' option" % self.name)
			return

		# // script options
		# ----------------------------------------------------------------
		match_condition = "contains"
		if "match-cond" in args:
			match_condition = args["match-cond"]["value"]
		reverse_match = False
		#multi_match = False
		if "match" in args:
			match_args = args["match"]["value"].split(",")
			reverse_match = "reverse" in match_args
			#multi_match = "multi" in match_args

		out_full_width = False
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

			if match_db_name is not None and match_db_name != db_name:
				continue
			if db.is_sys_table(table_name) and exclude_sysdbs:
				continue

			#table_columns = db.table_columns(db_conn, db_name, table_name)
			#print(table_columns)
			table_columns = db.columns(db_conn, db_name, table_name)
			table_columns = list(map(lambda n: n[1], table_columns))
			#print(table_columns)
			#for i in range(len(columns)):
			#	# convert tuple to list
			#	columns[i] = [*columns[i],]

			query = '''
				SELECT * FROM %s
			''' % table_name
			rows = db.query_db(db_conn, query)
			for row in rows:
				# convert tuple to list
				row = [*row,]
				
				row_list = []
				for i in range(len(table_columns)):
					match_found = False
					column_name = table_columns[i]
					column_value = row[i]

					if find_value is not None:
						if self.match_on_condition(find_value, column_value, match_condition):
							match_found = True

					column_value = str(column_value).rstrip()
					if not out_full_width and len(column_value) > 100:
						column_value = "%s...<STRIPPED>" % column_value[:100]

					if match_found:
						if not reverse_match:
							table_list.append([db_name, table_name, column_name, column_value])
					elif reverse_match:
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

		match_condition = "contains"
		if "match-cond" in args:
			match_condition = args["match-cond"]["value"]

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
		if db_name is None:
			if not db.table_exists(db_conn, table_name):
				print("[!] warning: %s; table not found - '%s'" % (self.name, table_name))
				return
		elif not db.table_exists_in_db(db_conn, db_name, table_name):
			print("[!] warning: %s; table in db not found - '%s.%s'" % (self.name, db_name, table_name))
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

				mod_column_value = str(field_value).rstrip()
				if not out_full_width and len(str(field_value)) > 100:
					mod_column_value = "%s...<STRIPPED>" % str(field_value)[:100]
				row_list.append(mod_column_value)

				if not multi_match:
					if field_name is not None:
						if not self.match_on_condition(field_name, column_name, match_condition):
							continue
					if self.match_on_condition(find_value, field_value, match_condition):
						match_found = True
				else:
					if field_name is not None:
						if not self.match_on_condition(field_name, column_name, match_condition):
							continue
					find_values = find_value.split("|")
					for match_on_value in find_values:
						if self.match_on_condition(match_on_value, field_value, match_condition):
							match_found = True
							break
			
			if match_found:
				if not reverse_match:
					table_list.append(row_list)
			elif reverse_match:
				table_list.append(row_list)

		self._output_table(table_list, headers, out_format)

	def match_on_condition(self, find_value, match_on_value, match_condition):
		match_found = False
		if "exact" == match_condition:
			if find_value.lower() == str(match_on_value).lower():
				match_found = True
		elif "contains" == match_condition:
			if find_value.lower() in str(match_on_value).lower():
				match_found = True
		elif "startswith" == match_condition:
			if str(match_on_value).lower().startswith(find_value.lower()):
				match_found = True
		elif "endswith" == match_condition:
			if str(match_on_value).lower().endswith(find_value.lower()):
				match_found = True
		elif "has-value" == match_condition:
			if len(str(match_on_value)) > 0:
				match_found = True
		return match_found

	def _output_table(self, table_list, headers, out_format=None):
		tablefmt='github'
		wrap_data = False
		out_json = False
		if "_internal.args.out_json" in self._extend:
			out_json = self._extend["_internal.args.out_json"]
		
		if out_json:
			self._output_table_as_json(table_list, headers, out_format)
			return

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

	def _output_table_as_json(self, table_list, headers, out_format=None):
		out_json = []
		for row in table_list:
			json_item = {}
			for i in range(len(headers)):
				key_name = headers[i]
				key_value = row[i]
				#print("%s: '%s'" % (key_name, key_value))
				json_item[key_name] = key_value
			out_json.append(json_item)
		#print(out_json)
		print(json.dumps(out_json))