#from core.sqlite_helper import *
import core.sqlite_helper as db

"""
CS_BEACON_STUB_MD5:CS_RELEASE_SHA256 (cobaltstrike.jar):CS_VERSION:CS_RELEASE_LEGITIMACY:COMMENT:META-DATA
"""
#def db_create_table_release(db_conn):
#	if db_table_exists(db_conn, "release"):
#		return False
#
#	try:
#		cur = db_conn.cursor()
#		cur.execute('''
#			CREATE TABLE release(
#				sha_256 integer,
#				md5 text,
#				filename text,
#				version text,
#				release_date text,
#				comment text
#				)''')
#		db_conn.commit()
#
#	except sqlite3.OperationalError:
#		return False
#
#	return True

def create_table_release(db_conn):
	if db.db_table_exists(db_conn, "release"):
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

	except db.Exception.OperationalError:
		return False

	return True

def release_exists(db_conn, sha_256):
	query_param = '''
		SELECT *
		FROM release
		WHERE sha_256 = ?
	'''
	query_data = (sha_256)

	cur = db_conn.cursor()
	cur.execute(query_param, query_data)
	if len(rows) == 1:
		return True
	return False
def add_release(db_conn, sha_256, filename, version, release_date, comment):
	try:
		cur = db_conn.cursor()
		query = """INSERT INTO release
				(sha_256, filename, version, release_date, comment) 
				VALUES (?, ?, ?, ?, ?);"""
		query_data = (sha_256, filename, version, release_date, comment)
		cur.execute(query, query_data)
		db_conn.commit()
		return True
	except db.Exception.OperationalError:
		return False
def release_row_as_dict(release_row):
	release_dict = {}
	release_dict["sha_256"] = release_row[0]
	release_dict["filename"] = release_row[1]
	release_dict["version"] = release_row[2]
	release_dict["release_date"] = release_row[3]
	release_dict["comment"] = release_row[4]
	return release_dict
def get_releases(db_conn):
	result = []
	rows = db.query_db(db_conn, 'SELECT * FROM release')
	for row in rows:
		result.append(release_row_as_dict(row))
	return result
def get_release(db_conn, sha_256):
	query_param = '''
		SELECT *
		FROM release
		WHERE sha_256 = ?
	'''
	param_data = (sha_256,)

	cur = db_conn.cursor()
	cur.execute(query_param, param_data)
	rows = cur.fetchall()
	if len(rows) == 1:
		return rows[0]
	return None

def del_release(db_conn, sha_256):
	query = '''
		DELETE FROM release WHERE sha_256 = ?
	'''
	try:
		cur = db_conn.cursor()
		cur.execute(query, (sha_256,))
		db_conn.commit()
		return True
	except db.Exception.OperationalError:
		return False

def add_hash_map(db_conn, md5, sha_256, comment):
	try:
		cur = db_conn.cursor()
		query = """INSERT INTO release
				(md5, sha_256, comment) 
				VALUES (?, ?, ?);"""
		query_data = (md5, sha_256, comment)
		cur.execute(query, query_data)
		db_conn.commit()
		return True
	except db.Exception.OperationalError:
		return False