Search in <table> under <column> for "keyword"

    returns all matching records
<#
	.name: basic-search-db
#
	.PARAMETER: table
	 table name to search in
	.PARAMETER: column
	 column name to search under
	.PARAMETER: keyword
	 phrase to search for
#	.PARAMETER: or_keyword
#	 phrase to search for in the 'comment' column
#>

SELECT
	t.*
FROM {{table}} t
WHERE
	t.{{column}} LIKE "%{{keyword}}%"