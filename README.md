# sqlbridge - Autobahn Database Service

Database Service for Autobahn

## Summary

A simple database access component for Autobahn. This component builds bridges to database backends making
them accessible to Autobahn via topics.  The component can be used in its raw form to build custom
Autobahn deployments, or, the convenience scripts that haver been included can be used to
connect an sqlbridge to an already operating Autobahn router.

Command to start database bridge:

```
usage: sqlbridge [-h] [-w WSOCKET] [-r REALM] [-v] [-u USER] [-s PASSWORD]
                 [-e ENGINE] [-d DSN] [-t TOPIC_BASE]

sql bridge for autobahn

optional arguments:
  -h, --help            show this help message and exit
  -w WSOCKET, --websocket WSOCKET
                        web socket definition, default is:
                        ws://127.0.0.1:8080/ws
  -r REALM, --realm REALM
                        connect to websocket using realm, default is: realm1
  -v, --verbose         Verbose logging for debugging
  -u USER, --user USER  connect to websocket as user, default is: db
  -s PASSWORD, --secret PASSWORD
                        users "secret" password
  -e ENGINE, --engine ENGINE
                        if specified, a database engine will be attached. Note
                        engine is rooted on --topic. Valid engine options are
                        PG, MYSQL or SQLITE
  -d DSN, --dsn DSN     if specified the database in dsn will be connected and ready.
                        dsns are unique to the engine being used.  Valid examples:
                        -----------
                        PG: dbname=autobahn host=192.168.200.230 user=autouser password=testpass
                        MYSQL: database=autobahn user=autouser password=passtest
                        SQLITE: Z
  -t TOPIC_BASE, --topic TOPIC_BASE
                        if you specify --dsn then you will need a topic to
                        root it on, the default com.db is fine.
```

valid DRIVERs are:
* PG9\_4	Postgres version v9.4b3 (PG)
* MYSQL14\_14	Mysql v14.14 (MYSQL)
* SQLITE3\_3\_8\_2	sqlite3 v3.8.2 (SQLITE)

valid topic_root would be the registration root.  As an example we can use 'com.db'.
what this does is set up the rpc with a prefix of com.db, and calls named:
connect, disconnect, query, operation, watch for the database engine. A complete example:

```sh
sqlbridge -v -e PG -t 'com.db' -d 'dbname=autobahn host=192.168.200.230 user=autouser'
or
sqlbridge -e MYSQL -t 'com.db' -d 'database=autobahn user=root'
or
sqlbridge -e SQLITE -t 'com.db' -d 'database=/tmp/ab'
```

For each of the aforementioned sqlbridge examples we have set up com.db.CALL rpc entry points:

* com.db.query      run a database query (results are expected, for example 'select ...')
* com.db.operation  run a database query (no results expected, for example 'insert into ...')
* com.db.watch      postgres has a LISTEN operator.  watch lets us specify what to listen for, and what to call when an event is triggered. The other drivers stub this out as a no op.

There are two other rpcs created as well, but, they are not needed in this context (because we specify the database we are connecting to on the sqlbridge command line). They are:
* com.db.connect    connect to a different db
* com.db.disconnect disconnect from a db

# Basic Documentation

## com.db.connect dsn

Connect to a database.  The dsn is formatted like the database driver requires (it is different for each type).  There are engine specific arguments, most of which can be seen in the example above.

## com.db.disconnect

Disconnect from the currently connected database.

## com.db.query query args

Run query on the database.  Argument substitution with supplied arguments.  Depending on the database the query will look different.  For example, postgres uses the realdictcursor, so inline substitution is done with %(name)s tags. Sqlite3 uses tags that look like :name. The result of the query is an array of dictionary rows.

## com.db.operation query args

Run an operation.  The difference between an operation and a query is that an operation does not expect an answer (like an insert statement).

## com.db.watch name

This function is only valid on a postgres database.  Postgres has a notify/listen feature that provides for async notification that something has happened in the database.  This watch function sets up a 'LISTEN' for one of these notifications.  When called, watch will create a new publication rooted on com.db.watch with an arbitrary random name. For example, say I want to know any time the employee data changes.  I do something like: sub\_topic = yield my\_app.call('com.db.watch','employee\_change').  This will return a topic string like com.db.watch.abcdefghij (random lower case characters).  I then subscribe to that.  Anytime a database client issues a NOTIFY employee\_change my subscription will get published with the payload.


