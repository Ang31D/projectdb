#!/usr/bin/python3
import argparse
import os
import config
import core.sqlite_helper as db
import core.cs_db as cs_db
import core.script_lib as lib
import importlib
from tabulate import tabulate
import csv
import json
from itertools import repeat
from collections import OrderedDict

""" select table from database
SELECT * FROM db_1.my_table
"""

def release_row_as_dict(release_row):
	release_dict = {}
	release_dict["sha_256"] = release_row[0]
	release_dict["filename"] = release_row[1]
	release_dict["version"] = release_row[2]
	release_dict["release_date"] = release_row[3]
	release_dict["comment"] = release_row[4]
	return release_dict
def release_ord_as_dict(release_ord):
	release_dict = {}
	release_dict["sha_256"] = release_ord["sha_256"]
	release_dict["filename"] = release_ord["filename"]
	release_dict["version"] = release_ord["version"]
	release_dict["release_date"] = release_ord["release_date"]
	release_dict["comment"] = release_ord["comment"]
	return release_dict

def get_db_file(args):
	if args.override_default_db_file is not None:
		return args.override_default_db_file

	script_dir = os.path.dirname(os.path.realpath(__file__))
	db_file = config.DB_SQLITE_FILE
	return os.path.join(script_dir, db_file)

#def get_releases(db_conn):
#	result = []
#	rows = db.query_db(db_conn, 'SELECT * FROM release')
#	for row in rows:
#		result.append(release_row_as_dict(row))
#	return result
def get_release(db_conn, sha_256):
	release_row = cs_db.get_release(db_conn, sha_256)
	if release_row is None:
		return release_row
	return release_row_as_dict(release_row)

def do_db_health_check(db_file):
	check_status = True
	if not os.path.isfile(db_file):
		print("[!] error: db_file: not found - '%s'" % db_file)
		check_status = False
		return check_status

	db_conn = db.connect(db_file)
	table_name = "release"
	if not db.table_exists(db_conn, table_name):
		print("[!] error: db_table missing - '%s'" % table_name)
		check_status = False

	db.close(db_conn)

	return check_status

def do_action_list_releases(db_conn, args):
	if args.out_json:
		print(json.dumps(cs_db.get_releases(db_conn)))
		return

	for release in cs_db.get_releases(db_conn):
		list_release(release, args.verbose_mode)
def do_action_list_release(db_conn, sha_256, verbose_mode):
	release = cs_db.get_release(db_conn, sha_256)
	if release is None:
		print("[!] warning: release not found - '%s'" % sha_256)
	else:
		list_release(release, verbose_mode)
def do_action_list_release_by_version(db_conn, version, verbose_mode):
	release_list = []
	for version in version.split(","):
		release_list += get_release_by_version(db_conn, version)
	for release in release_list:
		list_release(release, verbose_mode)
def get_releases_by_versions(db_conn, version_list):
	release_list = []
	for version in version_list:
		release_list += get_release_by_version(db_conn, version)
	return release_list
def get_release_by_version(db_conn, version):
	release_list = []
	for release in cs_db.get_releases(db_conn):
		if version.endswith("."):
			if release['version'].startswith(version):
				release_list.append(release)
		elif version.startswith("."):
			if release['version'].endswith(version):
				release_list.append(release)
		elif not "." in version:
			if version in release['version']:
				release_list.append(release)
		elif version == release['version']:
			release_list.append(release)
	return release_list
def list_release(release, verbose_mode):
	if verbose_mode:
		print(release)
	else:
		#(SHA256) 043dfa038873462039c28cdc3e0e3356de814157e5e851cc0931bfe2d96d7e8e, Licensed (cobaltstrike.jar) Cobalt Strike v4.8 (Release Date: 2023-02-28)
		out_format = "(SHA256) %s, Licensed (%s) Cobalt Strike v%s (Release Date: %s)" % (release['sha_256'], release['filename'], release['version'], release['release_date'])
		print(out_format)
def do_remove_release(db_conn, sha_256, verbose_mode, dry_mode):
	if dry_mode:
		print("[*] del release '%s'" % sha_256)
		print("[!] dry mode - would have deleted release '%s'" % sha_256)
		return
	
	if not db_del_release(db_conn, sha_256):
		print("[!] error: db_del_release(): status: failed - '%s'" % sha_256)
	else:
		print("[*] release removed - '%s'" % sha_256)
def do_action_truncate_table(db_conn, args):
	db_name = args.db_name
	table_name = args.table_name
	dry_mode = args.dry_mode

	if db_name is not None:
		table_name = "%s.%s" % (db_name, table_name)

	if not db.truncate_table(db_conn, table_name):
		print("[!] error: db_truncate_table(): status: failed - '%s'" % table_name)
		return
	print("[-] table truncated - '%s'" % table_name)
def do_action_drop_table(db_conn, args):
	db_name = args.db_name
	table_name = args.table_name
	dry_mode = args.dry_mode
	if db_name is None:
		db_name = 'main'

	if dry_mode:
		out_drop_statement = "'%s'" % table_name
		if db_name is not None:
			out_drop_statement = "'%s' from db('%s')" % (table_name, db_name)
		print("[*] drop table %s" % out_drop_statement)
		if not db.table_exists_in_db(db_conn, db_name, table_name):
			print("[!] dry mode warning: table not found - '%s'" % table_name)
		else:
			print("[!] dry mode - would have dropped %s" % out_drop_statement)
		return
	
	if db_name is not None:
		if not db.drop_table_from_database(db_conn, db_name, table_name):
			print("[!] error: db_drop_table_from_database(): status: failed - '%s.%s'" % (db_name, table_name))
			return
		print("[-] table dropped - '%s' from db('%s')" % (table_name, db_name))
	else:
		if not db.drop_table(db_conn, table_name):
			print("[!] error: db_drop_table(): status: failed - '%s'" % table_name)
		else:
			print("[-] table dropped - '%s'" % table_name)

def do_sub_actions_list_releases(db_conn, args):
	if args.release_sha256 is not None:
		sha_256 = args.release_sha256
		do_action_list_release(db_conn, sha_256, args.verbose_mode)
	elif args.release_version is not None:
		release_version = args.release_version
		do_action_list_release_by_version(db_conn, args.release_version, args.verbose_mode)
	else:
		do_action_list_releases(db_conn, args)

def do_sub_actions_remove_release(db_conn, args):
	dry_mode = args.dry_mode
	if args.release_sha256 is not None:
		sha_256 = args.release_sha256
		do_remove_release(db_conn, sha_256, args.verbose_mode, dry_mode)
	elif args.release_version is not None:
		version_list = args.release_version.split(",")
		release_list = get_releases_by_versions(db_conn, version_list)
		for release in release_list:
			#print(release)
			sha_256 = release["sha_256"]
			do_remove_release(db_conn, sha_256, args.verbose_mode, dry_mode)
			
			#break
			#do_remove_release(db_conn, sha_256, args.verbose_mode, dry_mode)
		#release_version = args.release_version

def do_action_enum_databases(db_conn, args):
	db_list = db.databases(db_conn)

	headers = ['seq','db']
	if args.schema:
		headers = ['seq','name','file']

	if args.verbose_mode:
		if args.count and not args.schema:
			headers.append('tables')
			for i in range(len(db_list)):
				# convert tuple to list
				db_list[i] = [*db_list[i],]
				#if not args.schema:
				db_list[i] = db_list[i][:-1]
				
				db_name = db_list[i][1]
				table_count = 0
				for table in db.tables(db_conn, db_name, None):
					table_name = table[1]
					if args.exclude_sysdbs and table_name in db.SYSDBS:
						continue
					table_count += 1
				db_list[i].append(table_count)
		else:
			for i in range(len(db_list)):
				# convert tuple to list
				db_list[i] = [*db_list[i],]
				if not args.schema:
					db_list[i] = db_list[i][:-1]
		
		if not args.out_json:
			print("[*] dbs: %s" % len(db_list))
			print(tabulate(db_list, headers=headers, tablefmt='github'))
		else:
			out_json = []
			for db_name in db_list:
				json_item = {}
				for i in range(len(headers)):
					json_item[headers[i]] = db_name[i]
				out_json.append(json_item)
			print(json.dumps(out_json))
		return

	if args.count:
		dbs_count = len(db_list)
		if not args.out_json:
			if args.verbose_mode:
				print("[*] dbs: %s" % dbs_count)
			else:
				print(dbs_count)
		else:
			out_json = {"count": dbs_count}
			print(json.dumps(out_json))
		return

	db_list = list(map(lambda n: n[1], db_list))
	#if len(db_list) == 1:
	#	db_list = [db_list]
	if not args.out_json:
		print("\n".join(db_list))
	else:
		out_json = []
		for db_name in db_list:
			out_json.append({"name": db_name})
		print(json.dumps(out_json))

def do_action_table_record_count(db_conn, args):
	db_name = args.db_name
	table_name = args.table_name

	filter_on_tables = []
	if table_name is not None:
		filter_on_tables = table_name.split(",")

	tables = db.tables(db_conn, db_name, None)

	table_list = []
	for table in tables:
		table_name = table[1]
		if args.exclude_sysdbs:
			if table_name in db.SYSDBS:
				continue
		if len(filter_on_tables) > 0:
			if table_name not in filter_on_tables:
				continue
		table_list.append(table)

	table_list = list(map(lambda n: n[0:2], table_list))
	headers = ['db', 'table', 'records']

	print("[*] db tables: %s" % len(table_list))
	for i in range(len(table_list)):
		# convert tuple to list
		table_list[i] = [*table_list[i],]
		table_name = table_list[i][1]
		record_count = db.record_count(db_conn, table_name)
		table_list[i].append(record_count)
	print(tabulate(table_list, headers=headers, tablefmt='github'))
def do_action_enum_tables(db_conn, args):
	db_name = args.db_name
	table_name = args.table_name

	filter_on_tables = []
	if table_name is not None:
		filter_on_tables = table_name.split(",")

	tables = db.tables(db_conn, db_name, None)

	table_list = []
	for table in tables:
		table_name = table[1]
		if table_name in db.SYSDBS:
			if args.exclude_sysdbs:
				continue
		if len(filter_on_tables) > 0:
			if table_name not in filter_on_tables:
				continue
		table_list.append(table)

	headers = ['schema', 'name', 'type', 'ncol', 'wr', 'strict']
	if not args.schema:
		table_list = list(map(lambda n: n[0:2], table_list))
		headers = ['db', 'table']

	if args.verbose_mode or args.schema:
		if not args.schema:
			headers.append('columns')
		if args.count and not args.schema:
			headers.append('records')
		
		for i in range(len(table_list)):
			# convert tuple to list
			table_list[i] = [*table_list[i],]

			table_name = table_list[i][1]
			if not args.schema:
				# add columns to table item
				table_columns = db.table_columns(db_conn, db_name, table_name)
				table_list[i].append(len(table_columns))
			if args.count and not args.schema:
				# add table record count to table item
				record_count = db.record_count(db_conn, table_name)
				table_list[i].append(record_count)
		
		if not args.out_json:
			print("[*] db tables: %s" % len(table_list))
			print(tabulate(table_list, headers=headers, tablefmt='github'))
		else:
			out_json = []
			for table_item in table_list:
				json_item = {}
				for i in range(len(headers)):
					json_item[headers[i]] = table_item[i]
				out_json.append(json_item)
			print(json.dumps(out_json))
		return

	if args.count:
		table_count = len(table_list)
		if not args.out_json:
			print(table_count)
		else:
			print(json.dumps({"count": table_count}))
		return

	if len(table_list) > 0:
		if db_name is None:
			table_list = list(map(lambda r: "%s.%s" % (r[0], r[1]), table_list))
		else:
			table_list = list(map(lambda r: "%s" % (r[1]), table_list))
		if not args.out_json:
			print('\n'.join(table_list))
		else:
			out_json = []
			for table_name in table_list:
				if "." in table_name:
					db_name = table_name.split(".")[0]
					table_name = table_name.split(".")[1]
					out_json.append({"db": db_name, "table": table_name})
				else:
					out_json.append({"table": table_name})
			print(json.dumps(out_json))
	
def do_action_enum_columns(db_conn, args):
	db_name = args.db_name
	table_name = args.table_name
	column_name = args.column_name

	table_names = []
	if table_name is not None:
		table_names = table_name.split(",")
	else:
		# no tables defined, get all tables (filters on database if specified)
		table_names = db.table_names(db_conn, db_name, None)
	# make list unique; may have duplicate tablename from different databases
	table_names = list(set(table_names))

	db_names = []
	if db_name is not None:
		db_names.append(db_name)
	else:
		# no databases defined, get all databases
		db_names = db.database_names(db_conn)
	
	filter_on_columns = []
	if column_name is not None:
		filter_on_columns = column_name.split(",")

	db_table_column_list = []
	for db_name in db_names:
		for table_name in table_names:
			# filter out system databases
			if args.exclude_sysdbs:
				if table_name in db.SYSDBS:
					continue

			columns = db.columns(db_conn, db_name, table_name)
			for i in range(len(columns)):
				# convert tuple to list
				columns[i] = [*columns[i],]

				colum_name = columns[i][1]
				if len(filter_on_columns) > 0:
					if colum_name not in filter_on_columns:
						continue
				# prefix column_info with db & table name
				columns[i].insert(0, table_name)
				columns[i].insert(0, db_name)

				db_table_column_list.append(columns[i])

	headers = ['db', 'table', 'cid', 'name', 'type', 'notnull', 'dflt_value', 'pk']
	if not args.schema:
		db_table_column_list = list(map(lambda n: [n[0], n[1], n[3]], db_table_column_list))
		headers = ['db', 'table', 'column']
		pass

	total_column_count = len(db_table_column_list)
	if args.verbose_mode or args.schema:
		if args.count:
			headers = ['db', 'table', 'columns']
			db_table_column = OrderedDict()
			for item in db_table_column_list:
				db_name = item[0]
				table_name = item[1]
				column_name = item[2]
				
				db_table = "%s.%s" % (db_name, table_name)
				if db_table not in db_table_column:
					db_table_column[db_table] = []
				db_table_column[db_table].append(column_name)
			
			total_column_count = 0
			db_table_column_list = []
			for db_table, column_names in db_table_column.items():
				db_name = db_table.split(".")[0]
				table_name = db_table.split(".")[1]
				column_count = len(column_names)
				total_column_count += column_count
				db_table_column_list.append([db_name, table_name, column_count])

		total_db_count = len(list(set(list(map(lambda n: n[0], db_table_column_list)))))
		total_table_count = len(list(set(list(map(lambda n: "%s.%s" % (n[0], n[1]), db_table_column_list)))))

		if not args.out_json:
			print("[*] db(%s) table(%s) columns: %s" % (total_db_count, total_table_count, total_column_count))
			print(tabulate(db_table_column_list, headers=headers, tablefmt='github'))
		else:
			out_json = []
			for db_table_column in db_table_column_list:
				json_item = {}
				for i in range(len(headers)):
					json_item[headers[i]] = db_table_column[i]
				out_json.append(json_item)
			print(json.dumps(out_json))
		return

	column_list = list(set(list(map(lambda n: n[2], db_table_column_list))))
	if len(column_list) > 0:
		if args.count:
			if not args.out_json:
				print(len(list(map(lambda n: n[2], db_table_column_list))))
			else:
				print(json.dumps({"count": len(column_list)}))
			return

		if not args.out_json:
			print('\n'.join(column_list))
		else:
			out_json = []
			for db_table_column in db_table_column_list:
				db_name = db_table_column[0]
				table_name = db_table_column[1]
				column_name = db_table_column[2]
				out_json.append({"db": db_name, "table": table_name, "column": column_name})
			print(json.dumps(out_json))

def do_action_dump_table_schema(db_conn, args):
	db_name = args.db_name
	table_name = args.table_name

	print("[*] db(%s) table('%s') schema:" % (db_name, table_name))
	table_schema = db.table_schema(db_conn, table_name)
	print(table_schema)

def do_action_dump_table_records(db_conn, args):
	table_name = args.table_name
	db_name = args.db_name
	if db_name is None:
		db_name = 'main'

	if table_name is None:
		print("[!] error: dump table - missing table")
		print("[!] (use '-T <table_name> [--schema])")
		return
	if "," in table_name:
			print("[!] error: dump table; multi tables not supported - '%s'" % table_name)
			return

	if args.schema:
		print("[*] db table('%s') schema:" % table_name)
		table_schema = db.table_schema(db_conn, table_name)
		if table_schema is not None:
			print(table_schema)
		return

	select_columns = ''
	if args.column_name is not None:
		table_columns = db.table_columns(db_conn, db_name, table_name)
		columns = args.column_name.split(",")
		for column in columns:
			column_name = column.strip()
			if column_name not in table_columns:
				continue
			if len(select_columns) > 0:
				select_columns += ","
			select_columns += column_name
	if len(select_columns) == 0:
		select_columns = '*'

	query = '''
		SELECT %s FROM %s
	''' % (select_columns, table_name)
	if args.limit is not None:
		query += " LIMIT %s" % args.limit
	if args.offset is not None:
		query += " OFFSET %s" % args.offset
	rows = db.query_db(db_conn, query)

	if args.count:
		record_count = 0
		if rows is not None:
			record_count = len(rows)
		if args.out_json:
			print(json.dumps({"count": record_count}))
		else:
			print(record_count)
		return

	#if rows is None:
	#	return

	headers = []
	if select_columns == '*':
		headers = db.table_columns(db_conn, db_name, table_name)
	else:
		headers = select_columns.split(",")

	if args.out_json:
		out_json = []
		for row in rows:
			json_item = {}
			for i in range(len(headers)):
				json_item[headers[i]] = row[i]
			out_json.append(json_item)
		print(json.dumps(out_json))
		return

	if args.verbose_mode:
		print("[*] db table('%s') entries: %s" % (table_name, len(rows)))
		table = []
		for row in rows:
			table.append(list(map(lambda n: n, row)))
		print(tabulate(table, headers=headers, tablefmt='github'))
		return

	for row in rows:
		print(row)

def do_action_query_db(db_conn, args):
	table_name = args.table_name
	#print("[*] db query")
	
	query = args.query
	#print(query)
	rows = db.query_db(db_conn, query)
	if rows is None:
		print("[!] do_action_query_db(): status: failed - '%s'" % query)
		return
	#print(rows)
	for row in rows:
		print(row)

def parse_query_template_file(template_file, verbose_mode):
	template = None
	if not os.path.isfile(template_file):
		return template

	with open(template_file) as f:
		template = {}
		template["path"] = template_file
		template["_raw"] = ''
		template["Description"] = ''
		template["Template"] = ''
		template["Query"] = ''
		template["Parameters"] = OrderedDict()
		template["StatusOK"] = True
		template["DebugInfo"] = {}
		template["DebugInfo"]["Log"] = []

		valid_properties = ["parameter"]
		start_tag_found = False
		end_tag_found = False

		line_count = -1
		previous_property = None
		for line in f.readlines():
			template["_raw"] += line
			line_count += 1
			if line.strip() == "<#":
				start_tag_found = True
				continue
			if line.strip() == "#>":
				end_tag_found = True
				continue

			# line part of description
			if not start_tag_found:
				template["Description"] += line
				continue
			
			# skip commented out and empty lines
			if line.lstrip().startswith("#") or len(line.strip()) == 0:
				continue

			# line part of property section
			if start_tag_found and not end_tag_found:
				# check for property
				if line.lstrip().startswith(".") and ":" in line:
					property_type = line.lstrip().split(".")[1].split(":")[0].lower()
					#if not property_type in valid_properties:
					#	template["StatusOK"] = False
					#	template["DebugInfo"]["Log"].append("[!] warning: unsupported property type '%s' in template '%s'" % (property_type, template_file))
					#	continue
					# parse property
					if property_type == "parameter":
						param_name = ':'.join(line.split(":")[1:]).strip()
						param = OrderedDict()
						param["name"] = param_name
						param["description"] = ''
						param["value"] = ''
						template["Parameters"][param["name"]] = param
						previous_property = param["name"]
						continue
				# add property description
				elif previous_property is not None:
					if previous_property in template["Parameters"]:
						param = template["Parameters"][previous_property]
						param["description"] = line.strip()
						template["Parameters"][param["name"]] = param
					else:
						#print("[!] warning: parse query template failed; missing parameter: '%s'" % previous_property)
						template["StatusOK"] = False
						template["DebugInfo"]["Log"].append("[!] warning: parse query template failed; missing parameter '%s' in template '%s'" % (previous_property, template_file))
			
			# line part of query template
			if end_tag_found:
				template["Template"] += line
		
	# remove last trailing new line
	template["_raw"] = template["_raw"].rstrip()
	# remove any starting or trailing whitespace/new line
	template["Description"] = template["Description"].strip()
	# remove any trailing whitespace/new line
	template["Template"] = template["Template"].rstrip()

	return template
def inspect_query_template(template, verbose_mode):
	print(template["Description"])
	print("")

	parameters = list(template["Parameters"].keys())

	if len(parameters) > 0:
		print("* Parameters")
		#print("-"*30)
		for i in range(len(parameters)):
			param_name = parameters[i]
			param = template["Parameters"][param_name]
			print("%s: %s" % (param["name"], param["description"]))

	print("")
	print("* Template")
	print("-"*30)
	print(template["Template"])
	print("-"*30)

	if not verbose_mode or verbose_mode:
		# output any defined template parameter (positions)
		print("")
		if len(parameters) > 0:
			print("* Parameter (position)")
			print("-"*30)
			for i in range(len(parameters)):
				param_name = parameters[i]
				param = template["Parameters"][param_name]
				print("%s: %s" % (i, param["name"]))
	if not verbose_mode:
		return
	
	print("-"*30)
	print("")
	print("")
		
	print("[**** Formatted Template ****]")
	print("")

	if template["Matching_Parameter_Inputs"]:
		if len(parameters) > 0:
			print("* Parameter (key/value pair)")
			print("-"*30)
			for i in range(len(parameters)):
				param_name = parameters[i]
				param = template["Parameters"][param_name]
				print("%s = %s" % (param["name"], param["value"]))

			print("")
			print("* Query (formatted)")
			print("-"*30)
			print(template["Query"])
			print("-"*30)
	else:
		# output defined template parameter (positions)
		if len(parameters) > 0:
			print("* Parameter (position)")
			print("-"*30)
			for i in range(len(parameters)):
				param_name = parameters[i]
				param = template["Parameters"][param_name]
				print("%s: %s" % (i, param["name"]))
		
		# output any passed parameter value (positions)
		print("")
		print("* Input (position)")
		print("-"*30)
		inputs = template["Inputs"]
		for i in range(len(inputs)):
			parameter_input = inputs[i]
			print("%s: %s" % (i, parameter_input))
def out_query_template_debug_info(template):
	for log_line in template["DebugInfo"]["Log"]:
		print(log_line)
def do_action_query_db_from_template(db_conn, args):
	if not os.path.isfile(args.query_from_file):
		print("[!] error: query template failed - file not found '%s'" % args.query_from_file)
		return

	template = parse_query_template_file(args.query_from_file, args.verbose_mode)
	if template is None:
		print("[!] error: query template failed - missing file content '%s'" % args.query_from_file)
		return
	if not template["StatusOK"]:
		print("[!] error: parse query template failed '%s'" % template["path"])
		for log_line in template["DebugInfo"]["Log"]:
			print(log_line)
		out_query_template_debug_info(template)
		return

	template["Inputs"] = args.template_parameters

	parameters = list(template["Parameters"].keys())

	template["Matching_Parameter_Inputs"] = True
	if len(template["Inputs"]) != len(parameters):
		template["StatusOK"] = False
		template["Matching_Parameter_Inputs"] = False
		if args.template_parameters is not None and not args.inspect_query_template:
			print("[!] warning: query template failed; incorrect num of param fields: '%s'" % template["path"])

			template["DebugInfo"]["Log"].append("[!] warning: query template failed; incorrect num of param fields: '%s'" % template["path"])
			return
	
	# // add input value to parameter & format query
	if template["Matching_Parameter_Inputs"]:
		query = template["Template"]
		for i in range(len(parameters)):
			param_name = parameters[i]
			param = template["Parameters"][param_name]
			# add input value to parameter
			param["value"] = template["Inputs"][i]
			# store updated parameter
			template["Parameters"][param["name"]] = param
			# format query
			query = query.replace("{{%s}}" % param["name"], param["value"])
		template["Query"] = query

	if args.inspect_query_template:
		inspect_query_template(template, args.verbose_mode)
		return

	query = template["Query"]
	rows = db.query_db(db_conn, query)
	if rows is None:
		#print("[!] do_action_query_db(): status: failed \n%s" % query)
		print("[!] do_action_query_db(): status: failed")
#		_raw_list = template["_raw"].split("\n")
#		_raw_list = list(map(lambda n: "#> %s" % n.strip(), _raw_list))
#		print('\n'.join(_raw_list))
		return
	#print(rows)
	for row in rows:
		print(row)

def list_databases(db_conn, verbose_mode):
	query = 'PRAGMA database_list'
	rows = db.query_db(db_conn, query)
	for row in rows:
		if not verbose_mode:
			db_name = row[1]
			print(db_name)
		else:
			print(row)

def do_action_attach_db(db_conn, args):
	db_list = args.attach_db.split(",")
	#for attach_db in db_list:
	#	if not ":" in attach_db:
	#		print("[!] error: attach database() failed - '%s'" % args.attach_db)
	#		print("[!] (use '-A <db_name>:<db_file>')")
	#		return
	for attach_db in db_list:
		db_name = None
		db_file = None
		if ":" in attach_db:
			db_name, db_file = attach_db.split(":")
		else:
			db_file = attach_db
			if attach_db.endswith(".db"):
				db_file = attach_db
				db_name = ".".join(os.path.basename(attach_db).split(".")[:-1])
			else:
				db_name = os.path.basename(attach_db)
				db_file = attach_db
		if not os.path.isfile(db_file):
			print("[!] warning: attach database(%s) failed - file not found '%s'" % (db_name, db_file))
			continue
		if not db.attach_db(db_conn, db_name, db_file):
			print("[!] warning: attach database(%s) failed - '%s'" % (db_name, db_file))

def export_db_table_schema(db_conn, out_file, table_name):
	table_schema = db.table_schema(db_conn, table_name)
	print(table_schema)
	with open(out_file, 'w') as f:
		f.write(table_schema)
def export_db_table(db_conn, out_file, db_name, table_name):
	print("[*] export table '%s'" % table_name)
	if db_name is None:
		db_name = 'main'

	if not db.table_exists_in_db(db_conn, db_name, table_name):
		print("[!] error: table not found - '%s'" % table_name)
		return

	query_param = '''
		SELECT *
		FROM %s
	''' % table_name
	param_data = ()
	rows = db.execute(db_conn, query_param, param_data, True)

	column_list = db.table_columns(db_conn, db_name, table_name)
	#print(column_list)

	#print(rows)
	with open(out_file, 'w', newline='') as f:
		csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		#csv_writer.writerow(column_list)
		for row in rows:
			csv_writer.writerow(row)
		
	print("[*] table '%s' exported -> '%s'" % (table_name, out_file))
	#for row in rows:
	#	print(row)
def do_db_export(db_conn, args):
	if args.table_name is None:
		print("[!] error: export database - missing table")
		print("[!] (use '-T <table_name> [--schema])")
		return

	out_file = args.db_export
	table_name = args.table_name
	if not args.schema:
		export_db_table(db_conn, out_file, args.db_name, args.table_name)
	else:
		export_db_table_schema(db_conn, out_file, args.table_name)

def do_db_import(db_conn, args):
	table_name = args.table_name
	in_file = args.db_import
	db_name = args.db_name
	if db_name is None:
		db_name = "main"

	if args.table_name is None:
		print("[!] error: import database - missing table")
		print("[!] (use '-T <table_name>)")
		return
	if not os.path.isfile(in_file):
		print("[!] warning: import database - file not found '%s'" % in_file)
		print("[!] (use '--import <file>)")
		return

	column_list = db.table_columns(db_conn, db_name, table_name)
	table_columns = ', '.join(column_list)
	quest_values = ', '.join(list(repeat("?", len(column_list))))

	query_param = """INSERT INTO %s
				(%s) 
				VALUES (%s);""" % (table_name, table_columns, quest_values)

	cur = db_conn.cursor()
	with open(in_file) as f:
		csv_reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		#if args.verbose_mode:
		#	for row in csv_reader:
		#		print(row)
		cur.executemany(query_param, csv_reader)
		db_conn.commit()

		print("[*] table '%s' imported <- '%s'" % (table_name, in_file))

		#print(f.readlines())
	cur.close()

def do_define_db(db_conn, args):
	definition_file = args.define_db

	table_definition = db.table_definition_from_file(definition_file)
	if table_definition is None:
		print("[!] do_define_db() failed to get definition: '%s'" % definition_file)
		return

	table_name = db.get_table_from_definition(table_definition)
	if table_name is None:
		print("[!] do_define_db() invalid table definition: '%s'\n%s" % (definition_file, table_definition))
		return

	"""
		rename table name of defined table definition
	"""
	if args.table_name is not None and table_name != args.table_name:
		print("[*] do_define_db: renaming defined table '%s' to '%s'" % (table_name, args.table_name))
		table_definition = db.rename_table_definition(table_definition, args.table_name)
		if table_definition is None:
			table_definition = db.table_definition_from_file(definition_file)
			print("[!] error: do_define_db; rename table definition failed - new table name '%s'\n%s" % (definition_file, table_definition))
			return
		table_name = args.table_name
		#print(table_name)
		#return

	if db.table_exists(db_conn, table_name):
		print("[!] do_define_db() table already exists - '%s'" % table_name)
		return

	if not db.define_db(db_conn, table_definition):
		print("[!] define_db() status: failed: '%s'\n%s" % (definition_file, table_definition))
		return

	print("[*] define_db() status: success: '%s'\n%s" % (definition_file, table_definition))

def create_db(args):
	db_file = args.create_db
	if db.db_exists(db_file):
		print("[!] warning: database already exists - '%s'" % db_file)
		return False
	db_conn = db.create_db(db_file)
	if db_conn is None:
		print("[!] error: create database failed - '%s'" % db_file)
		return False
	db.close(db_conn)
	print("[*] database created - '%s'" % db_file)
	return True

def connect_db(db_file, args):
	if not db.db_exists(db_file):
		print("[!] error: database failed to connect - missing file '%s'" % db_file)
		return None
	db_conn = db.connect(db_file)
	if db_conn is None:
		print("[!] error: database failed to connect - '%s'" % db_file)
		return None
	return db_conn

def do_action_script_help(args):
	if args.script_help is None:
		if args.verbose_mode:
			print("[!] warning: no script defined")
		return

	lib_root_dir = lib.root_dir()

	if not os.path.isdir(lib_root_dir):
		if args.verbose_mode:
			print("[!] error: folder not found - '%s'" % (lib_root_dir))
		return

	help_scripts = {}
	#script_repo = lib.repos()
	extend_script = None
	repo_dir = lib_root_dir
	if args.extend_script is not None:
		extend_script = args.extend_script
		repo_dir = args.extend_script
	script_repo = lib.repos(repo_dir)
	
	help_script = lib.parse_script_help(args.script_help)
#	print(help_script)
	for script_name in help_script:
#		print("script_name: %s" % script_name)
		#script = lib.get_script_from_repo_dir(script_name, repo_dir)
		script = lib.get_script_from_repo(script_name, script_repo)
		if script is None:
			print("[!] warning: failed to get script by name - '%s'" % script_name)
			continue
#		print("********** output script **********")
#		print(script)
		script_path = script["path"]
		#script_path = lib.get_script_path_by_name(script_name)
#		print(script_path)
		if script_path in script_repo:
			#module_path = lib.script_path_as_module_path(script_path)
			module_path = script["module_path"]
			if module_path is None:
				print("[!] warning: failed to convert script as module path - '%s'" % script_path)
				continue
			module = lib.get_script_module(module_path)
			script_module = module.script()
			script_module.extend({"_internal.script": script})
			script_module.extend({"_internal.verbose_mode": args.verbose_mode})
			script_module.help()
		else:
			print("[!] warning: script not found - '%s'" % script_path)

def do_action_run_script(db_conn, args):
	if args.run_scripts is None:
		if args.verbose_mode:
			print("[!] warning: no script defined")
		return

	lib_root_dir = lib.root_dir()

	if not os.path.isdir(lib_root_dir):
		if args.verbose_mode:
			print("[!] error: folder not found - '%s'" % (lib_root_dir))
		return

	run_script_args = lib.parse_raw_script_args(args.run_scripts, args.script_args)
	#run_script_args = lib.parse_script_args(args.run_scripts, args.script_args)
#	print("-"*88)
#	print(run_script_args)
#	print("-"*88)
	if run_script_args is None:
		print("[!] error: lib.parse_script_args(args.run_scripts, args.script_args)")
		return

	
	repo_dir = lib_root_dir
	if args.extend_script is not None:
		#extend_script = os.path.realpath(args.extend_script)
		repo_dir = args.extend_script
	script_repo = lib.repos(repo_dir)

	for script_path in script_repo:
		script = script_repo[script_path]
		if script["name"] in run_script_args:
			run_script_item = run_script_args[script["name"]]
			module = lib.get_script_module(script["module_path"])
			
			if module is None:
				print("[!] warning: failed to get script module - '%s'" % script["module_path"])
				continue
			
			script_module = module.script()
			script_module.extend({"_internal.script": script})
			script_module.extend({"_internal.verbose_mode": args.verbose_mode})
			if "sqlite" in script_module.requirements:
				script_module.extend({"sqlite.db_conn": db_conn})
				#script_module.extend({"sqlite": {"db_conn", db_conn}})
			if "script-repo" in script_module.requirements:
				script_module.extend({"script.repo-dir": repo_dir})
			module_args = run_script_args[script["name"]]["args"]
			script_module.run(module_args)
		#else:
		#	print("Script '%s' unknown" % script["name"])

#	print("[!] do_action_run_script() - NOT IMPLEMENTED")

def main(args):
	if args.script_help is not None:
		do_action_script_help(args)
		return

	if args.create_db is not None:
		print("# create_db")
		if not create_db(args):
			return
		# we can both create and define the database table
		if args.define_db is None:
			return

	db_file = get_db_file(args)
	db_conn = connect_db(db_file, args)
	if db_conn is None:
		print("[!] error: database failed to connect - '%s'" % db_file)
		return

	if args.run_scripts is not None:
		do_action_run_script(db_conn, args)
		db.close(db_conn)
		return

	"""
		Database Management
	"""
#	if args.create_db is not None:
#		print("# create_db")
#		if not create_db(args):
#			return
#		# we can both create and define the database table
#		if args.define_db is None:
#			return

	if args.define_db is not None:
		print("# do_define_db")
		if args.create_db is not None:
			db_conn = connect_db(args.create_db, args)
			if db_conn is None:
				print("[!] error: database failed to connect - '%s'" % args.create_db)
				return
		do_define_db(db_conn, args)
		# we can both define and populate the database table
		if args.db_import is None:
			db.close(db_conn)
			return

	if args.db_import is not None:
		print("# do_db_import")
		do_db_import(db_conn, args)
		db.close(db_conn)
		return

	if args.attach_db is not None:
		#print("# do_action_attach_db")
		do_action_attach_db(db_conn, args)

	if args.db_export is not None:
		print("# do_db_export")
		do_db_export(db_conn, args)
		return

	if args.action_truncate_table:
		print("# do_action_truncate_table")
		do_action_truncate_table(db_conn, args)
		return
	if args.action_drop_table:
		print("# do_action_drop_table")
		do_action_drop_table(db_conn, args)
		return

	"""
		Enumerate Database
	"""
	if args.action_enum_databases:
		#print("# do_action_enum_databases")
		do_action_enum_databases(db_conn, args)
		db.close(db_conn)
		return
	if args.action_enum_tables:
		#print("# do_action_enum_tables")
		do_action_enum_tables(db_conn, args)
		db.close(db_conn)
		return
	if args.action_enum_columns:
		#print("# do_action_enum_columns")
		do_action_enum_columns(db_conn, args)
		db.close(db_conn)
		return

	if args.action_dump_table_entries:
		#print("# do_action_dump_table_records")
		do_action_dump_table_records(db_conn, args)
		db.close(db_conn)
		return

	if args.schema and (args.table_name is not None and "," not in args.table_name) and (args.db_name is not None or db.db_count(db_conn) == 1):
		print("# do_action_dump_table_schema")
		do_action_dump_table_schema(db_conn, args)
		db.close(db_conn)
		return

	if args.table_name is not None and args.count:
		print("# do_action_table_record_count")
		do_action_table_record_count(db_conn, args)
		db.close(db_conn)
		return

	if args.query is not None:
		print("# do_action_query_db")
		do_action_query_db(db_conn, args)
		db.close(db_conn)
		return
	if args.query_from_file is not None:
		print("# do_action_query_db_from_template")
		do_action_query_db_from_template(db_conn, args)
		db.close(db_conn)
		return

	"""
		Stub Release Management
	"""
	if not do_db_health_check(db_file):
		print("[!] health check failed")
		return

	#if args.list_releases:
	#	do_sub_actions_list_releases(db_conn, args)

	#if args.action_remove:
	#	do_sub_actions_remove_release(db_conn, args)
	#	return

	print("[!] warning: no action was executed!")

	print("[*] status - total changes: %s" % db_conn.total_changes)
	db.close(db_conn)


if __name__ == '__main__':
	""" Verify features:
	OK - * --dbs # do_action_enum_databases: -v, --count, --json, --exclude-sysdbs
	OK - * --tables # do_action_enum_tables: -v --count, --json, --exclude-sysdbs, -D <db_name>, -T <table_name>, --schema
	OK - * --columns # do_action_enum_columns: -v --count, --json, --exclude-sysdbs, -D <db_name>, -T <table_name>, -C <column_name>, --schema
	OK - * --create # create_db: --create <file.db>
	* --define # do_define_db: --db <file.sql>
	* --import # do_db_import: --db <file.db>, -D <db_name>, -T <table_name>
	* --export # do_db_export: --db <file.db>, -D <db_name>, -T <table_name>
	"""
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Mgmt tool - Cobalt Strike Stub Release Information Database (CSRID)")
#	parser.add_argument('-L', '--list-releases', dest='list_releases', action='store_true', help="List Licensed Cobalt Strike (cobaltstrike.jar) Releases")
#	parser.add_argument('-r', '--select-release', metavar='<sha256>', dest='release_sha256', help="Specify specific release")
#	parser.add_argument('-V', '--select-version', metavar='<version>', dest='release_version', help="Select release(s) by version, supports format: 'x.y', 'x.', 'y.'" +
#		"\n(separate with comma for multiple versions)" +
#		"\n\n")
	
	parser.add_argument('--db', metavar='<file.db>', dest='override_default_db_file', help="Connect to database, override default <DB_SQLITE_FILE> ('config.py')")
	parser.add_argument('-A', '--attach-dbs', metavar='[<db_name>:]<file.db>[,...]', dest='attach_db', help="Attach database file with defined name, attach multiple dbs separated by comma" +
		"\n\n")

	parser.add_argument('-q', metavar='<query>', dest='query', help="Run query against the database")
	parser.add_argument('--template', metavar='<file>', dest='query_from_file', help="Run query template against the database")
	parser.add_argument('-p', metavar='<param>', dest='template_parameters', nargs='+', default=[], help="Parameter(s) for query template")
	parser.add_argument('--show', dest='inspect_query_template', action='store_true', help="Show query template description, use '-v' to show parameters" +
		"\n\n")

	parser.add_argument('--dbs', dest='action_enum_databases', action='store_true', help="Enumerate databases; use '-v' to out in table-format or '--json' for json-format, supports '--count'")
	parser.add_argument('--tables', dest='action_enum_tables', action='store_true', help="Enumerate database tables")
	parser.add_argument('--columns', dest='action_enum_columns', action='store_true', help="Enumerate database table columns")
	parser.add_argument('--schema', dest='schema', action='store_true', help="Show schema for dbs, tables and columns")
	parser.add_argument('--exclude-sysdbs', dest='exclude_sysdbs', action='store_true', help="Exclude system databases when enumerating tables (sqlite_schema, sqlite_temp_schema)")
	parser.add_argument('--count', dest='count', action='store_true', help="Output count")
	parser.add_argument('--dump', dest='action_dump_table_entries', action='store_true', help="Dump database table entries")
	parser.add_argument('--limit', metavar='<row_count>', dest='limit', type=int, help="Constrain the number of rows returned when using '--dump'")
	#parser.add_argument('--offset', metavar='<offset>', dest='offset', type=int, help="Offset where '--limit' should start")
	parser.add_argument('--offset', metavar='<offset>', dest='offset', type=int, help="Define the start of returned rows, use '--limit'")
	parser.add_argument('-D', metavar='<DB>', dest='db_name', help="Select database")
	parser.add_argument('-T', metavar='<TBL>', dest='table_name', help="Select database table(s)")
	parser.add_argument('-C', metavar='<COL>', dest='column_name', help="Select database table column(s)" +
		"\n\n")
	
	parser.add_argument('--create', metavar='<file.db>', dest='create_db', help="Create an empty database file")
	parser.add_argument('--define', metavar='<file.sql>', dest='define_db', help="Define database through definition file")
	parser.add_argument('--import', metavar='<file>', dest='db_import', help="Import from file, use '-T' to specify table")
	parser.add_argument('--export', metavar='<file>', dest='db_export', help='Export to file, use \'-T\' to specify table (add \'--schema\' for schema)' +
		"\n\n")

	#parser.add_argument('--rm', dest='action_remove', action='store_true', help="Remove from database, combine with '-r' or '-V'")
	parser.add_argument('--trunc-table', dest='action_truncate_table', action='store_true', help="Remove all records from a table, use '-T' to specify table")
	parser.add_argument('--drop-table', action='store_true', dest='action_drop_table', help="Drop table from database, use '-T' to specify table" +
		"\n\n")

	#<Lua scripts> is a comma separated list of directories, script-files or script-categories
	parser.add_argument('--script', metavar='<script_name>', dest='run_scripts', help="Run script(s) against the database; comma separated list")
	parser.add_argument('--script-args', metavar='<script_name>.<script_arg>=\'<value>\'', dest='script_args', nargs='+', help="provide arguments to scripts; comma separated list." +
		"\nuse '<script_name>.help' to show help about script")
	parser.add_argument('--ext-script', metavar='<folder>', dest='extend_script', help="Adds another \"scripts\" directory; comma separated list")
	parser.add_argument('--script-help', metavar='<script_name>', dest='script_help', help="Show help about scripts. Comma-separated list of" +
		"\nscript-files or script-categories." +
		"\n\n")
	

	parser.add_argument('--json', dest='out_json', action='store_true', help="Output as json")
	parser.add_argument('-v', dest='verbose_mode', action='store_true', help="Verbose output")
	parser.add_argument('--dry', dest='dry_mode', action='store_true', help="dry mode - do not commit to database" +
		"\n\n")

	args = parser.parse_args()
	main(args)