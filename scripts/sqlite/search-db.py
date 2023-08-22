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
		help_output += "\n%s" % "    find='<value>'          - value to search for; if omitted, match on any value"
		help_output += "\n%s" % "    look-for='<type>'       - what to find; valid types: 'db', 'table', 'column', 'field' (default),"
		help_output += "\n%s" % "                              db-schema, table-schema, column-schema"
		help_output += "\n%s" % "    db='<db_name>'          - db to search from or filter on"
		help_output += "\n%s" % "    table='<table_name>'    - table to search in or filter on"
		help_output += "\n%s" % "    column='<column_name>'  - column to match field value on or filter on; comma separated list"
		help_output += "\n"
		"""
			'match' options; conditionalizes the 'find' match
		"""
		help_output += "\n%s" % "    * Match"
		help_output += "\n%s" % "      match-cond='<cond>'   # match condition against ('find' option) <value>:"
		help_output += "\n%s" % "        contains            - <field> contains <string> (default)"
		help_output += "\n%s" % "        exact               - <field> match on exact <string>"
		help_output += "\n%s" % "        startswith          - <field> starts with <string>"
		help_output += "\n%s" % "        endswith            - <field> ends with <string>"
		help_output += "\n%s" % "        has-value           - <field> is not blank"
		help_output += "\n%s" % "        eq, lt, le, gt, ge  - <field> ==, <, <=, >, >= <num>"
		help_output += "\n"

		help_output += "\n%s" % "      match='<option>'      # comma separated list of options; available options:"
		help_output += "\n%s" % "        multi-value         - match on multiple ('find' option) values; values separated by '|'"
		help_output += "\n%s" % "        reverse             - negative match on 'find' value"
		help_output += "\n"
		help_output += "\n%s" % "      multi-delim='<char>'  - single character delimiter; used with match=multi-value"
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
			'output' options; controls the output
		"""
		help_output += "\n%s" % "    * Output"
		help_output += "\n%s" % "      out-column=<column>   - comma separated list of columns to output"
		help_output += "\n%s" % "      limit=<num>           - limit output to number or rows"
		help_output += "\n"
		help_output += "\n%s" % "      format='<option>'     # one option only; available options:"
		help_output += "\n%s" % "        no-columns          - skip output of columns"
		help_output += "\n%s" % "        wrap                - as 'no-columns' + wraps output; replace char '\\n' with '\\n\\t'"
		help_output += "\n%s" % "        csv                 - output in csv format (delimiter ',')"
		help_output += "\n%s" % "        json                - output in json format"
		help_output += "\n\n"

		help_output += "\n%s" % " * Examples"
		help_output += "\n%s" % "   --script search-db --script-args db=db/csrid.db options='exclude-sysdbs,full-width'"
		help_output += "\n"
		help_output += "\n%s" % "   Search on multi value match"
		help_output += "\n%s" % "   %s" % ("-"*len("Search on multiple value match"))
		help_output += "\n%s" % "   find records in 'hash_map' table that match on either 'jsonl' or 'virustotal' in the 'comment' column"
		help_output += "\n%s" % "   --script-args table=hash_map column=comment find='jsonl,virustotal' match=multi-value multi-delim=,"
		help_output += "\n"
		help_output += "\n%s" % "   find records in 'hash_map' table that does not match on 'jsonl' and 'virustotal' in the 'comment' column"
		help_output += "\n%s" % "   --script-args table=hash_map column=comment find='jsonl,virustotal' match=reverse,multi-value, multi-delim=,"
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
		if 'db' in args:
			db_name = args['db']['value']
		
		table_name = None
		if 'table' in args:
			table_name = args['table']['value']

		column_name = None
		if 'column' in args:
			column_name = args['column']['value']

		look_for = "field"
		if "look-for" in args:
			look_for = args["look-for"]["value"]

		match_condition = None
		if "match-cond" in args:
			match_condition = args["match-cond"]["value"]

		db_conn = self._extend["sqlite.db_conn"]
		if db_conn is None:
			return

		if   "db" == look_for:
			self._locate_db_table_column(db_conn, db_name, table_name, column_name, args)
		elif "table" == look_for:
			self._locate_db_table_column(db_conn, db_name, table_name, column_name, args)
		elif "column" == look_for:
			self._locate_db_table_column(db_conn, db_name, table_name, column_name, args)
		elif "db-schema" == look_for:
			self._locate_db_table_column_schema(db_conn, db_name, table_name, column_name, args)
		elif "table-schema" == look_for:
			self._locate_db_table_column_schema(db_conn, db_name, table_name, column_name, args)
		elif "column-schema" == look_for:
			self._locate_db_table_column_schema(db_conn, db_name, table_name, column_name, args)
		elif "field" == look_for:
			if find_value is None:
				if match_condition is None or match_condition != "has-value":
					print("[!] error: %s; required 'find' option missing during '%s' look-up" % (self.name, look_for))
					return
			if table_name is None:
				#self._search_db_for_record_field(db_conn, db_name, find_value, exclude_sysdbs, args)
				self._search_db_for_record_field(db_conn, db_name, column_name, find_value, exclude_sysdbs, args)
			else:
				self._search_db_for_record_in_table(db_conn, db_name, table_name, find_value, args)
		else:
			print("[!] warning: %s; look-for type not supported - '%s'" % (self.name, look_for))

		db.close(db_conn)

	def _search_db_for_record_field(self, db_conn, filter_on_db_name, filter_on_column, find_value, exclude_sysdbs, args):
		tables = db.tables(db_conn, None, None)

		#if find_value is None:
		#	print("[!] error: %s; missing 'find' option" % self.name)
		#	return

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
		limit_row_numbers = None
		if "limit" in args:
			limit_value = args["limit"]["value"]
			if limit_value.isnumeric():
				limit_row_numbers = int(limit_value)

		filter_by_columns = []
		if filter_on_column is not None:
			for column_name in filter_on_column.split(","):
				if column_name.strip() not in filter_by_columns:
					filter_by_columns.append(column_name.strip())
		# ----------------------------------------------------------------

		table_list = []
		for table in tables:
			db_name = table[0]
			table_name = table[1]

			if filter_on_db_name is not None and filter_on_db_name != db_name:
				continue
			if exclude_sysdbs and db.is_sys_table(table_name):
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

					if len(filter_by_columns) > 0 and column_name not in filter_by_columns:
						continue

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

		if limit_row_numbers is not None:
			table_list = table_list[:limit_row_numbers]
		headers = ['db', 'table', 'column', 'value']
		self._output_table(table_list, headers, out_format)

	def _locate_db_table_column_schema(self, db_conn, locate_db, locate_table, locate_column, args):
		# // script options
		# ----------------------------------------------------------------
		look_for = None
		if "look-for" in args:
			look_for = args["look-for"]["value"]
			if look_for.endswith("-schema"):
				look_for = look_for[0:len(look_for)-len("-schema")]
		
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
			multi_match = "multi-value" in match_args
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
		limit_row_numbers = None
		if "limit" in args:
			limit_value = args["limit"]["value"]
			if limit_value.isnumeric():
				limit_row_numbers = int(limit_value)
		# ----------------------------------------------------------------

		if look_for is None: # this should never happen
			print("[!] warning: %s; locate type not defined" % (self.name))
			print("(use 'look-for=<type>')")
			return
		
		headers = []
		rows = []
		if   "db" == look_for:
			headers = ['seq', 'name', 'file']
			#rows = db.db_schema_from_pragma(db_conn, locate_db)
			rows = db.db_schema_from_pragma(db_conn, None)
		elif "table" == look_for:
			headers = ['schema', 'name', 'type', 'ncol', 'wr', 'strict']
			#rows = db.table_schema_from_pragma(db_conn, locate_db, locate_table)
			rows = db.table_schema_from_pragma(db_conn, None, None)
		elif "column" == look_for:
			headers += ['schema', 'table', 'cid', 'name', 'type', 'notnull', 'dflt_value', 'pk']
			#rows = db.column_schema_from_pragma(db_conn, locate_db, locate_table, locate_column)
			rows = db.column_schema_from_pragma(db_conn, None, None, None)
		else:
			print("[!] error: %s; invalid locate type - '%s'" % (self.name, look_for))
			return

		if rows is None:
			print("[!] error: %s; failed to fetch schema for '%s'" % (self.name, look_for))
			return

		# filter on db, table, column
		filter_by_dbs = []
		if locate_db is not None:
			filter_by_dbs = locate_db.split(",")
		filter_by_tables = []
		if locate_table is not None:
			filter_by_tables = locate_table.split(",")
		filter_by_columns = []
		if locate_column is not None:
			filter_by_columns = locate_column.split(",")
		# column index pos on db, table, column for filter
		index_pos_db = -1
		index_pos_table = -1
		index_pos_column = -1
		if "db" == look_for:
			index_pos_db = 0
		if "table" == look_for:
			index_pos_db = 0
			index_pos_table = 1
		elif "column" == look_for:
			index_pos_db = 0
			index_pos_table = 1
			index_pos_column = 3

		table_list = []
		#print("filter_by_columns: %s" % filter_by_columns)
		#print("index_pos_column: %s" % index_pos_column)
		for row in rows:
			match_found = False

			if exclude_sysdbs and index_pos_table >= 0 and db.is_sys_table(row[index_pos_table]):
				continue

			if find_value is None:
				if len(filter_by_dbs) > 0 and index_pos_table >= 0:
					if row[index_pos_db] not in filter_by_dbs:
						continue
			if len(filter_by_tables) > 0 and index_pos_table >= 0:
				if row[index_pos_table] not in filter_by_tables:
					continue
			if "column" != look_for or find_value is None:
				if len(filter_by_columns) > 0 and index_pos_column >= 0:
					#print(row[index_pos_column])
					if row[index_pos_column] not in filter_by_columns:
						#print("skip - %s" % row)
						continue

			if find_value is not None:
				row_item = []
				for i in range(len(row)):
					field = row[i]
					field_name = headers[i]
					row_item.append(field)
					if locate_column is not None and field_name not in locate_column.split(","):
						continue
					if not multi_match:
						if self.match_on_condition(find_value, field, match_condition):
							match_found = True
					else:
						for match_on_value in find_value.split(multi_delim):
							if self.match_on_condition(match_on_value, field, match_condition):
								match_found = True
								break
			else:
				match_found = True

			if find_value is not None:
				if match_found:
					if reverse_match:
						match_found = False
				elif reverse_match:
					match_found = True
				
			if match_found:
				#table_list.append(row_item)
				table_list.append(row)

		if limit_row_numbers is not None:
			table_list = table_list[:limit_row_numbers]
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
			multi_match = "multi-value" in match_args
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
		limit_row_numbers = None
		if "limit" in args:
			limit_value = args["limit"]["value"]
			if limit_value.isnumeric():
				limit_row_numbers = int(limit_value)
		# ----------------------------------------------------------------

		if look_for is None: # this should never happen
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
				if not multi_match:
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
					row_item.append(db_name)
				elif "table" == look_for:
					row_item.append(db_name)
					row_item.append(table_name)
				elif "column" == look_for:
					row_item.append(db_name)
					row_item.append(table_name)
					row_item.append(column_name)
				if len(row_item) > 0:
					dup_id = '|'.join(row_item)
					if dup_id in dup_list:
						continue
					table_list.append(row_item)
					dup_list.append(dup_id)

		headers = ['db']
		if   "db" == look_for:
			headers = ['db']
		elif "table" == look_for:
			headers = ['db', 'table']
		elif "column" == look_for:
			headers = ['db', 'table', 'column']

		if limit_row_numbers is not None:
			table_list = table_list[:limit_row_numbers]
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
			multi_match = "multi-value" in match_args
		multi_delim = "|"
		if "multi-delim" in args:
			multi_delim = args["multi-delim"]["value"]
			if len(multi_delim) != 1:
				print("[!] error: %s; invalid \"multi-delim\" option value - '%s'" % (self.name, multi_delim))
				return

		out_format = None
		if "format" in args:
			out_format = args["format"]["value"]
		limit_row_numbers = None
		if "limit" in args:
			limit_value = args["limit"]["value"]
			if limit_value.isnumeric():
				limit_row_numbers = int(limit_value)
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

		if limit_row_numbers is not None:
			table_list = table_list[:limit_row_numbers]
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
		elif "empty" == match_condition:
			if len(str(match_on_value)) == 0:
				match_found = True
		elif self._is_number_conditions(match_condition):
			if str(match_on_value).isnumeric() and str(find_value).isnumeric():
				match_found = self._match_on_number_condition(int(find_value), int(match_on_value), match_condition)
		return match_found
	def _is_number_conditions(self, condition):
		num_cond_list = ["ne", "eq", "lt", "le", "gt", "ge"]
		return condition in num_cond_list
	def _match_on_number_condition(self, find_num, match_on_num, match_condition):
		match_found = False

		if not self._is_number_conditions(match_condition):
			return match_found
		if not str(find_num).isnumeric() or not str(match_on_num).isnumeric():
			return match_found

		if "eq" == match_condition:
			if int(match_on_num) == int(find_num):
				match_found = True
		#elif "ne" == match_condition:
		#	if int(match_on_num) != int(find_num):
		#		match_found = True
		elif "lt" == match_condition:
			if int(match_on_num) < int(find_num):
				match_found = True
		elif "le" == match_condition:
			if int(match_on_num) <= int(find_num):
				match_found = True
		elif "gt" == match_condition:
			if int(match_on_num) > int(find_num):
				match_found = True
		elif "ge" == match_condition:
			if int(match_on_num) >= int(find_num):
				match_found = True
		return match_found

	def _output_table(self, table_list, headers, out_format=None):
		tablefmt='github'
		wrap_data = False
		out_json_format = False

		if out_format is not None:
			if out_format == "no-columns" or out_format == "wrap":
				tablefmt='plain'
				headers = []
			if out_format == "wrap":
				wrap_data = True

		if "json" == out_format:
			out_json_format = True
		elif "_internal.args.out_json" in self._extend:
			out_json_format = self._extend["_internal.args.out_json"]
		if out_json_format:
			self._output_table_as_json(table_list, headers)
			return

		if out_format == "csv":
			self._output_table_as_csv(table_list, headers, ",")
			return
		
		out_data = tabulate(table_list, headers=headers, tablefmt=tablefmt)
		if wrap_data:
			print(out_data.replace("\\n", "\n\t"))
		else:
			print(out_data)

	def _output_table_as_csv(self, table_list, headers, delimiter=None):
		field_delim = ","
		if delimiter is not None:
			field_delim = ","
		if len(field_delim) != 1:
			print("[!] warning: %s; invalid field delimiter length - '%s'" % (self.name, field_delim))

		table_data = []
		#headers = list(map(lambda n: '"%s"' % n, headers))
		table_data.append(field_delim.join(headers))
		for row in table_list:
			row_value = ""
			for field in row:
				field_value = field
				if "," in str(field):
					field_value = '"%s"' % str(field)
				#field_value = '"%s"' % field
				if len(row_value) > 0:
					row_value += field_delim
				row_value += str(field_value)
			table_data.append(row_value)
		print('\n'.join(table_data))

	def _output_table_as_json(self, table_list, headers, out_format=None):
		out_json = []
		for row in table_list:
			json_item = {}
			for i in range(len(headers)):
				key_name = headers[i]
				key_value = row[i]
				json_item[key_name] = key_value
			out_json.append(json_item)
		print(json.dumps(out_json))