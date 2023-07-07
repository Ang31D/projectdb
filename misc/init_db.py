#!/usr/bin/python3
import sys
import os
#sys.path.insert(1, '../')
#sys.path.append('../')
APP_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(APP_DIR)

#from core.sqlite_helper import *
import core.sqlite_helper as db
import core.cs_db as cs_db
#from application.app.folder.file import func_name
import config


def db_create_table_release(db_conn):
	if db_table_exists(db_conn, "release"):
		return False

	try:
		cur = db_conn.cursor()
		cur.execute('''
			CREATE TABLE release(
				sha_256 text,
				filename text,
				version text,
				release_date text,
				comment text
				)''')
		db_conn.commit()

	except sqlite3.OperationalError:
		return False

	return True

def db_create_table_stub_to_release(db_conn):
	if db_table_exists(db_conn, "stub_map"):
		return False

	try:
		cur = db_conn.cursor()
		cur.execute('''
			CREATE TABLE stub_map(
				md5 text,
				sha_256 text
				)''')
		db_conn.commit()

	except sqlite3.OperationalError:
		return False

	return True



def create_db_table_from_definition(db_conn, table_definition):
	#// CREATE TABLE stub_map(
	if not table_definition.startswith("CREATE TABLE ") and "(" in table_definition:
		print("db_create_table() invalid table definition: '%s'" % table_definition)
		return False

	table_name = table_definition[0:table_definition.index("(")]
	table_name = table_name.split(" ")[2]
	#print("db_create_table() table_name: '%s'" % table_name)
	#if db.table_exists(db_conn, "stub_map"):
	if db.table_exists(db_conn, table_name):
		print("[!] db_create_table() table already exists - '%s'" % table_name)
		return False
	print("db_create_table() DOES NOT EXISTS - table_name: '%s'" % table_name)
	#return False

	try:
		cur = db_conn.cursor()
		cur.execute(table_definition)
		db_conn.commit()

	except sqlite3.OperationalError:
		return False

	return True

def release_record_as_dict(record):
	record_dict = {}
	record_dict["sha_256"] = record[0]
	record_dict["filename"] = record[1]
	record_dict["version"] = record[2]
	record_dict["release_date"] = record[3]
	record_dict["comment"] = record[4]
	return record_dict
def hash_map_record_as_dict(record):
	record_dict = {}
	record_dict["md5"] = record[0]
	record_dict["sha_256"] = record[1]
	record_dict["comment"] = record[2]
	return record_dict

#def add_known_releases(db_conn):
def init_known_releases(db_conn):
	# (sha_256, md5, filename, version, release_date)
	#// create known releases
	records = []
	records.append(['20bebed19e0e1639c7b719d5db70c574417707063fcd669e60349a89485d392b','cobaltstrike.jar','3.7','2017-03-15',''])
	records.append(['77ad57b1f29569773350b228d065135c8745949bd80ee7ba59f3b01c27895bfb','cobaltstrike.jar','3.8','2017-05-23',''])
	records.append(['57090f6e3a5721e4d00ebc57b65bf3c8ca29809f8dd5ac0ac5b31c0ece76f02d','cobaltstrike.jar','3.9','2017-09-20',''])
	records.append(['a9bde8f8694f1bcd23a3ec9774fe00ba4fad6d80bbf14aadf48940a9cd20b0e5','cobaltstrike.jar','3.9','2017-09-21','bug fix'])
	records.append(['20aacc907dddaa528ebfe5fa74743a5366d52dd28073ecfd05a4922fb23ada40','cobaltstrike.jar','3.9','2017-09-26','bug fix II'])
	records.append(['f6fff191e05e3e1345db600f2731fea6324b10e57023e38e712e7f648e8643eb','cobaltstrike.jar','3.10','2017-12-11',''])
	records.append(['f3e3e645141ffcd5089816f90dee24ded30386277343f3254df05c837a6068aa','cobaltstrike.jar','3.11','2018-04-09',''])
	records.append(['d37ab96af1cc3f4a98ba63804138f644508e632f3791e3cfdde745d307bff5d9','cobaltstrike.jar','3.11','2018-05-24',''])
	records.append(['4349e9195e083573fca38a35f7327b6d2a95538101bef9c9efdb7476d4642d8c','cobaltstrike.jar','3.12','2018-09-06',''])
	records.append(['2c44e5426c41798dd11764cf64bf493ff81d4e77e3ed96dd6c65cf3333bdd809','cobaltstrike.jar','3.13','2019-01-02',''])
	records.append(['283d9074bc089841b9ef39100928ed240721c3dbce003c93f4283d71d7a3a410','cobaltstrike.jar','3.14','2019-05-02',''])
	records.append(['0e3e7ace7f6f99b9227e9e644ae0e7469e79e4fc746a8f632940e35821a74da9','cobaltstrike.jar','3.14','2019-05-04','bug fixes'])
	records.append(['558f61bfab60ef5e6bec15c8a6434e94249621f53e7838868cdb3206168a0937','cobaltstrike.jar','4.0','2019-12-05',''])
	records.append(['10fe0fcdb6b89604da379d9d6bca37b8279f372dc235bbaf721adfd83561f2b3','cobaltstrike.jar','4.0','2020-02-22','[bug fixes'])
	records.append(['1f2c29099ba7de0f7f05e0ca0efb58b56ec422b65d1c64e66633fa9d8f469d4f','cobaltstrike.jar','4.1','2020-06-25',''])
	records.append(['56a53682084c46813a5157d73d7917100c9979b67e94b05c1b3244469e7ee07a','cobaltstrike.jar','4.2','2020-11-06',''])
	records.append(['02fa5afe9e58cb633328314b279762a03894df6b54c0129e8a979afcfca83d51','cobaltstrike.jar','4.3','2021-03-03',''])
	records.append(['c3c243e6218f7fbaaefb916943f500722644ec396cf91f31a30c777c2d559465','cobaltstrike.jar','4.3','2021-03-17','bug fixes'])
	records.append(['7af9c759ac78da920395debb443b9007fdf51fa66a48f0fbdaafb30b00a8a858','cobaltstrike.jar','4.4','2021-08-04',''])
	records.append(['a5e980aac32d9c7af1d2326008537c66d55d7d9ccf777eb732b2a31f4f7ee523','cobaltstrike.jar','4.5','2021-12-14',''])
	records.append(['939aa731685ac5c2632e4790daf034110ae4aa7237a6db72c7bba219bd450727','cobaltstrike.jar','4.6','2022-04-12',''])
	records.append(['09e30bde7602cfa3358c0b1c9124079c77181c81c4ef0ef4f6789e24a3f07d5b','cobaltstrike.jar','4.6.1','2022-05-23',''])
	records.append(['c1cda82b39fda2f77c811f42a7a55987adf37e06a522ed6f28900d77bbd4409f','cobaltstrike.jar','4.7','2022-08-17',''])
	records.append(['2387c9ead13876d70a332c4ce57c4c090232d346376e174c703b38cda39f3f8f','cobaltstrike.jar','4.7.1','2022-09-16',''])
	records.append(['5cc4e4df156579cbd01a09dd4c1daca513113f771cb5034a22c1e1dfb3ba424b','cobaltstrike.jar','4.7.2','2022-10-17',''])
	records.append(['043dfa038873462039c28cdc3e0e3356de814157e5e851cc0931bfe2d96d7e8e','cobaltstrike.jar','4.8','2023-02-28',''])
	for record in records:
		release_dict = release_record_as_dict(record)
		print("[+] insert record - %s" % release_dict)
		sha_256 , filename, version, release_date, comment = record
		cs_db.add_release(db_conn, sha_256, filename, version, release_date, comment)
	"""
	db_add_release(db_conn, '20bebed19e0e1639c7b719d5db70c574417707063fcd669e60349a89485d392b','cobaltstrike.jar','3.7','2017-03-15','')
	db_add_release(db_conn, '77ad57b1f29569773350b228d065135c8745949bd80ee7ba59f3b01c27895bfb','cobaltstrike.jar','3.8','2017-05-23','')
	db_add_release(db_conn, '57090f6e3a5721e4d00ebc57b65bf3c8ca29809f8dd5ac0ac5b31c0ece76f02d','cobaltstrike.jar','3.9','2017-09-20','')
	db_add_release(db_conn, 'a9bde8f8694f1bcd23a3ec9774fe00ba4fad6d80bbf14aadf48940a9cd20b0e5','cobaltstrike.jar','3.9','2017-09-21','bug fix')
	db_add_release(db_conn, '20aacc907dddaa528ebfe5fa74743a5366d52dd28073ecfd05a4922fb23ada40','cobaltstrike.jar','3.9','2017-09-26','bug fix II')
	db_add_release(db_conn, 'f6fff191e05e3e1345db600f2731fea6324b10e57023e38e712e7f648e8643eb','cobaltstrike.jar','3.10','2017-12-11','')
	db_add_release(db_conn, 'f3e3e645141ffcd5089816f90dee24ded30386277343f3254df05c837a6068aa','cobaltstrike.jar','3.11','2018-04-09','')
	db_add_release(db_conn, 'd37ab96af1cc3f4a98ba63804138f644508e632f3791e3cfdde745d307bff5d9','cobaltstrike.jar','3.11','2018-05-24','')
	db_add_release(db_conn, '4349e9195e083573fca38a35f7327b6d2a95538101bef9c9efdb7476d4642d8c','cobaltstrike.jar','3.12','2018-09-06','')
	db_add_release(db_conn, '2c44e5426c41798dd11764cf64bf493ff81d4e77e3ed96dd6c65cf3333bdd809','cobaltstrike.jar','3.13','2019-01-02','')
	db_add_release(db_conn, '283d9074bc089841b9ef39100928ed240721c3dbce003c93f4283d71d7a3a410','cobaltstrike.jar','3.14','2019-05-02','')
	db_add_release(db_conn, '0e3e7ace7f6f99b9227e9e644ae0e7469e79e4fc746a8f632940e35821a74da9','cobaltstrike.jar','3.14','2019-05-04','bug fixes')
	db_add_release(db_conn, '558f61bfab60ef5e6bec15c8a6434e94249621f53e7838868cdb3206168a0937','cobaltstrike.jar','4.0','2019-12-05','')
	db_add_release(db_conn, '10fe0fcdb6b89604da379d9d6bca37b8279f372dc235bbaf721adfd83561f2b3','cobaltstrike.jar','4.0','2020-02-22','[bug fixes')
	db_add_release(db_conn, '1f2c29099ba7de0f7f05e0ca0efb58b56ec422b65d1c64e66633fa9d8f469d4f','cobaltstrike.jar','4.1','2020-06-25','')
	db_add_release(db_conn, '56a53682084c46813a5157d73d7917100c9979b67e94b05c1b3244469e7ee07a','cobaltstrike.jar','4.2','2020-11-06','')
	db_add_release(db_conn, '02fa5afe9e58cb633328314b279762a03894df6b54c0129e8a979afcfca83d51','cobaltstrike.jar','4.3','2021-03-03','')
	db_add_release(db_conn, 'c3c243e6218f7fbaaefb916943f500722644ec396cf91f31a30c777c2d559465','cobaltstrike.jar','4.3','2021-03-17','bug fixes')
	db_add_release(db_conn, '7af9c759ac78da920395debb443b9007fdf51fa66a48f0fbdaafb30b00a8a858','cobaltstrike.jar','4.4','2021-08-04','')
	db_add_release(db_conn, 'a5e980aac32d9c7af1d2326008537c66d55d7d9ccf777eb732b2a31f4f7ee523','cobaltstrike.jar','4.5','2021-12-14','')
	db_add_release(db_conn, '939aa731685ac5c2632e4790daf034110ae4aa7237a6db72c7bba219bd450727','cobaltstrike.jar','4.6','2022-04-12','')
	db_add_release(db_conn, '09e30bde7602cfa3358c0b1c9124079c77181c81c4ef0ef4f6789e24a3f07d5b','cobaltstrike.jar','4.6.1','2022-05-23','')
	db_add_release(db_conn, 'c1cda82b39fda2f77c811f42a7a55987adf37e06a522ed6f28900d77bbd4409f','cobaltstrike.jar','4.7','2022-08-17','')
	db_add_release(db_conn, '2387c9ead13876d70a332c4ce57c4c090232d346376e174c703b38cda39f3f8f','cobaltstrike.jar','4.7.1','2022-09-16','')
	db_add_release(db_conn, '5cc4e4df156579cbd01a09dd4c1daca513113f771cb5034a22c1e1dfb3ba424b','cobaltstrike.jar','4.7.2','2022-10-17','')
	db_add_release(db_conn, '043dfa038873462039c28cdc3e0e3356de814157e5e851cc0931bfe2d96d7e8e','cobaltstrike.jar','4.8','2023-02-28','')
	"""
def add_hash_map(db_conn):
	# (sha_256, md5, filename, version, release_date)
	#// create known releases
	records = []
	#records.append(['222b8f27dbdfba8ddd559eeca27ea648','7af9c759ac78da920395debb443b9007fdf51fa66a48f0fbdaafb30b00a8a858','Cobalt Strike Java archive file hash, ref: https://www.virustotal.com/gui/file/7af9c759ac78da920395debb443b9007fdf51fa66a48f0fbdaafb30b00a8a858/details'])
	#records.append(['04e0a11be59147a8d73d2b3e9fea832c','a5e980aac32d9c7af1d2326008537c66d55d7d9ccf777eb732b2a31f4f7ee523','Cobalt Strike Java archive file hash, ref: https://www.virustotal.com/gui/file/a5e980aac32d9c7af1d2326008537c66d55d7d9ccf777eb732b2a31f4f7ee523/details'])
	#records.append(['653c0bdcb0d8ac0a12250441835871be','b899a9a4c42ec0f193389faf0b06ba04e954ea4348e120964c677b0cd602cdb6','Cobalt Strike Java archive file hash, ref: https://www.virustotal.com/gui/file/b899a9a4c42ec0f193389faf0b06ba04e954ea4348e120964c677b0cd602cdb6/details'])

	records.append(['222b8f27dbdfba8ddd559eeca27ea648','7af9c759ac78da920395debb443b9007fdf51fa66a48f0fbdaafb30b00a8a858','Cobalt Strike Java archive file hash'])
	records.append(['04e0a11be59147a8d73d2b3e9fea832c','a5e980aac32d9c7af1d2326008537c66d55d7d9ccf777eb732b2a31f4f7ee523','Cobalt Strike Java archive file hash'])
	records.append(['653c0bdcb0d8ac0a12250441835871be','b899a9a4c42ec0f193389faf0b06ba04e954ea4348e120964c677b0cd602cdb6','Cobalt Strike Java archive file hash'])
	#print(records)
	for record in records:
		hash_map_dict = hash_map_record_as_dict(record)
		print("[+] insert record - %s" % hash_map_dict)
		md5, sha_256, comment = record
		cs_db.add_hash_map(db_conn, md5, sha_256, comment)

db_file = os.path.join(APP_DIR, config.DB_SQLITE_FILE)
if db.db_exists(db_file):
	print("[!] warning: database file exists - '%s" % db_file)
	#exit()
db_conn = None
db.create_db(db_file)
db_conn = db.connect(db_file)

table_definitions = []
table_definitions.append(os.path.join(APP_DIR, "db_definitions/table_release.sql"))
#table_definitions.append(os.path.join(APP_DIR, "db_definitions/table_release_copy.sql"))
#table_definitions.append(os.path.join(APP_DIR, "db_definitions/table_stager_stub.sql"))
table_definitions.append(os.path.join(APP_DIR, "db_definitions/table_hash_map.sql"))

for definition_file in table_definitions:
	table_definition = db.table_definition_from_file(definition_file)
	if not create_db_table_from_definition(db_conn, table_definition):
		print("[!] error: db_create_table(<table_definition>): status: failed - '%s'\n%s" % (definition_file, table_definition))

#definition_file = "db_definitions/table_release.py"
#table_definition = cs_db.table_definition_from_file(definition_file)
#definition_file = "db_definitions/table_release_copy.py"
#table_definition = cs_db.table_definition_from_file(definition_file)
#if not create_db_table_from_definition(db_conn, table_definition):
#	print("[!] error: db_create_table(<table_definition>): status: failed\n%s" % table_definition)
#
#print(table_definition)
#if not create_db_table_from_definition(db_conn, table_definition):
#	print("[!] error: db_create_table(<table_definition>): status: failed\n%s" % table_definition)
#	pass

init_known_releases(db_conn)
add_hash_map(db_conn)
db.close(db_conn)
exit()

""" check prerequisites
	fail on:
	* check if
		database exists
		and 'release' table exists
"""
if db_exists(db_file):
	db_conn = db.connect(db_file)
	if db_table_exists(db_conn, "release"):
		db_name = os.path.basename(db_file)
		print("[!] error: db('%s'): table already exists - '%s'" % (db_name, "release"))
		db.close(db_conn)
		exit()
	else:
		print("[!] warning: db_file: already exists - '%s'" % db_file)
	
""" init db
	create database
"""
db_name = os.path.basename(db_file)
#print("[*] create_db(%s)" % db_file)
if not db.create_db(db_file):
	db_name = os.path.basename(db_file)
	print("[!] error: create_db('%s'): status: failed, path: '%s'" % (db_name, db_file))
	exit()
print("['*'] db.connect('%s'): filepath: '%s'" % (db_name, db_file))
db_conn = db.connect(db_file)
print("[*] db_create_table(%s)" % "release")
db_create_table_release(db_conn)

print("[*] db_create_table(%s)" % "release")
print("[*] init_known_releases")
init_known_releases(db_conn)

rows = db_query(db_conn, 'SELECT * FROM release')
print("inserted releases: %s" % len(rows))
#print("[*] db_add_release(%s)" % "release")
db.close(db_conn)