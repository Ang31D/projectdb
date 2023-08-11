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
		help_output += "\n%s" % "      multi-delim='<char>'  - specify a single character delimiter; used with match=multi"
		help_output += "\n"

		"""
			'extra' options;  to control the output
		"""
		help_output += "\n%s" % "    * Extra options"
		help_output += "\n%s" % "      options='<option>'    # comma separated list of options; available options:"
		help_output += "\n%s" % "        exclude-sysdbs      - exclude system tables during search"
		help_output += "\n%s" % "        full-width          - does not strip field value when more then 100 in length"
		help_output += "\n"

		"""
			'format' options; controls the output
		"""
		help_output += "\n%s" % "    * Output Format"
		help_output += "\n%s" % "      format='<option>'     # one option only; available options:"
		help_output += "\n%s" % "        no-columns          - skip output of columns"
		help_output += "\n%s" % "        wrap                - as 'no-columns' + wrap the output; replace char '\\n' with '\\n\\t'"
		help_output += "\n%s" % "        json                - output in json format"
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

		find_value = None
		if "find" in args:
			find_value = args["find"]["value"]

		exclude_sysdbs = False
		if "options" in args:
			option_args = args["options"]["value"].split(",")
			exclude_sysdbs = "exclude-sysdbs" in option_args

		db_name = None
		if 'db-name' in args:
			db_name = args['db-name']['value']
		
		table_name = None
		if 'table' in args:
			table_name = args['table']['value']

		column_name = None
		if 'column' in args:
			column_name = args['column']['value']

		look_for = "field"
		if "look-for" in args:
			look_for = args["look-for"]["value"]

		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return

		if   "db" == look_for:
			self._locate_db_table_column(db_conn, db_name, table_name, column_name, args)
		elif "table" == look_for:
			self._locate_db_table_column(db_conn, db_name, table_name, column_name, args)
		elif "column" == look_for:
			self._locate_db_table_column(db_conn, db_name, table_name, column_name, args)
		elif "field" == look_for:
			if find_value is None:
				print("[!] error: %s; required 'find' option missing during '%s' look-up" % (self.name, look_for))
				return
			if table_name is None:
				self._search_db_for_record_field(db_conn, db_name, find_value, exclude_sysdbs, args)
			else:
				self._search_db_for_record_in_table(db_conn, db_name, table_name, find_value, args)
		else:
			print("[!] warning: %s; look-for type not supported - '%s'" % (self.name, look_for))

		db.close(db_conn)

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

			table_columns = db.columns(db_conn, db_name, table_name)
			table_columns = list(map(lambda n: n[1], table_columns))

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

	def _locate_db_table_column(self, db_conn, locate_db, locate_table, locate_column, args):
		# // script options
		# ----------------------------------------------------------------
		look_for = None
		if "look-for" in args:
			look_for = args["look-for"]["value"]
		
		find_value = None
		if "find" in args:
			find_value = args["find"]["value"]

		match_condition = "contains"
		if "match-cond" in args:
			match_condition = args["match-cond"]["value"]

		reverse_match = False
		multi_match = False
		if "match" in args:
			match_args = args["match"]["value"].split(",")
			reverse_match = "reverse" in match_args
			multi_match = "multi" in match_args
		multi_delim = "|"
		if "multi-delim" in args:
			multi_delim = args["multi-delim"]["value"]
			if len(multi_delim) != 1:
				print("[!] error: %s; invalid \"multi-delim\" option value - '%s'" % (self.name, multi_delim))
				return

		exclude_sysdbs = False
		if "options" in args:
			option_args = args["options"]["value"].split(",")
			exclude_sysdbs = "exclude-sysdbs" in option_args

		out_format = None
		if "format" in args:
			out_format = args["format"]["value"]
		# ----------------------------------------------------------------
		if look_for is None:
			print("[!] warning: %s; locate type not defined" % (self.name))
			print("(use 'look_for=<type>')")
			return
		if   "db" == look_for:
			pass
		elif "table" == look_for:
			pass
		elif "column" == look_for:
			pass
		else:
			print("[!] error: %s; invalid locate type - '%s'" % (self.name, look_for))
			return
		
		rows = db.locate_db_table_column_using_pragma(db_conn, locate_db, locate_table, locate_column)

		dup_list = []
		table_list = []
		for row in rows:
			row_list = []
			match_found = False

			db_name = row[0]
			table_name = row[1]
			column_name = row[2]

			if exclude_sysdbs and db.is_sys_table(table_name):
				continue

			match_on = ''
			if   "db" == look_for:
				match_on = db_name
			elif "table" == look_for:
				match_on = table_name
			elif "column" == look_for:
				match_on = column_name
			if find_value is not None:
				#if not self.match_on_condition(find_value, match_on, match_condition):
				#	continue
				if not multi_match:
					#if field_name is not None:
					#	if not self.match_on_condition(field_name, match_on, match_condition):
					#		continue
					if self.match_on_condition(find_value, match_on, match_condition):
						match_found = True
				else:
					for match_on_value in find_value.split(multi_delim):
						if self.match_on_condition(match_on_value, match_on, match_condition):
							match_found = True
							break
			else:
				match_found = True
			
			if match_found:
				if reverse_match:
					match_found = False
			elif reverse_match:
				match_found = True
			
			if match_found:
				row_item = []
				if   "db" == look_for:
					#table_list.append([db_name])
					row_item.append(db_name)
				elif "table" == look_for:
					#table_list.append([db_name, table_name])
					row_item.append(db_name)
					row_item.append(table_name)
				elif "column" == look_for:
					#table_list.append([db_name, table_name, column_name])
					row_item.append(db_name)
					row_item.append(table_name)
					row_item.append(column_name)
				if len(row_item) > 0:
					dup_id = '|'.join(row_item)
					if dup_id in dup_list:
						continue
					table_list.append(row_item)
					dup_list.append(dup_id)

			#table_list.append(row)
		#headers = ['db', 'table', 'column']
		headers = ['db']
		if   "db" == look_for:
			headers = ['db']
		elif "table" == look_for:
			headers = ['db', 'table']
		elif "column" == look_for:
			headers = ['db', 'table', 'column']
		self._output_table(table_list, headers, out_format)

	def _search_db_for_record_in_table(self, db_conn, match_db_name, table_name, find_value, args):
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
		multi_delim = "|"
		if "multi-delim" in args:
			multi_delim = args["multi-delim"]["value"]
			if len(match_delim) != 1:
				print("[!] error: %s; invalid \"multi-delim\" option value - '%s'" % (self.name, multi_delim))
				return

		out_format = None
		if "format" in args:
			out_format = args["format"]["value"]
		# ----------------------------------------------------------------

		#tables = db.tables(db_conn, match_db_name, table_name)

		table_list = []
		if match_db_name is None:
			if not db.table_exists(db_conn, table_name):
				print("[!] warning: %s; table not found - '%s'" % (self.name, table_name))
				return
		elif not db.table_exists_in_db(db_conn, match_db_name, table_name):
			print("[!] warning: %s; table in db not found - '%s.%s'" % (self.name, match_db_name, table_name))
			return
		
		table_columns = []
		if match_db_name is None:
			#table_columns = db.column_names(db_conn, table_name)
			table_columns = db.get_table_columns(db_conn, table_name)
		else:
			table_columns = db.table_columns(db_conn, match_db_name, table_name)
		#print("-" * 88)
		#data = db.pragma_table_info(db_conn, table_name)
		#print(data)
		#data = db.table_schema_from_pragma(db_conn, table_name)
		#data = db.table_schema_from_pragma(db_conn, None)
		#print(data)
		#data = db.get_table_column_schema(db_conn, table_name)
		#print(data)
		#data = db.get_table_columns(db_conn, table_name)
		#print(data)
		#data = db.locate_table_dbs(db_conn, table_name)
		#print(data)
		#data = db.pragma_table_list_join_info(db_conn)
		##data = db.all_db_table_column_list(db_conn)
		#print(data)
		#rows = db.locate_db_table_column_using_pragma(db_conn, None, None, None)
		#for row in rows:
		#	print(row)
		#print("-" * 88)
		#print("")
		if len(table_columns) == 0:
			if match_db_name is None:
				print("[!] warning: %s; table columns not found - '%s'" % (self.name, table_name))
			else:
				print("[!] warning: %s; table columns in db not found - '%s.%s'" % (self.name, match_db_name, table_name))
			return
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
					for match_on_value in find_value.split(multi_delim):
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