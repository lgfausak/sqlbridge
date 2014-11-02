# sqlbridge - Autobahn Database Service

Database Service for Autobahn

## Summary

A simple database access mechanism for Autobahn.  This mechanism operates in two ways.
* management mode
* operating mode

### management mode
Management mode provides an Autobahn component that you can run giving you the ability to
create database services (operating modes) on the fly.  In this mode you simply get access
to 2 rpc calls:
* adm.db.start
start a new database bridge.
* adm.db.stop
stop a database bridge.
When run in this mode no database access is provided.  Instead, the service registers rpc calls for the 
administration of database bridges.

Command to start database bridge:

```python
yield self.call('adm.db.start', 'DRIVER', 'topic_root')
```

valid DRIVERs are:
* PG9\_4	Postgres version v9.4b3 (PG alias)
* MYSQL14\_14	Mysql v14.14 (MYSQL alias)
* SQLITE3\_3\_8\_2	sqlite3 v3.8.2 (SQLITE alias)

valid topic_root would be the registration root.  As an example we can use 'com.db'.
what this does is set up the rpc with a prefix of com.db, and calls named:
connect, disconnect, query, operation, watch for the database engine. A complete example:

```python
yield self.call('adm.db.start', 'PG', 'com.db')
```

After calling adm.db.start you would have a new database bridge at com.db. 

The rpc calls in this example would be :

* com.db.connect    start a postgres connection, the dsn is passed, dsn in psycopg2 format
* com.db.disconnect stop the postgres connection
* com.db.query      run a database query async
* com.db.operation  run a database query (no results expected)
* com.db.watch      postgres has a LISTEN operator.  watch lets us specify what to listen for, and what to call when an event is triggered. I think that other drivers will probably just stub this out (unless they have a notify/listen behavior)

The class also has a main routine which will connect to your Autobahn realm as required.  There is a convenience startup feature in the main routine to establish a connection with a database if desired.

```
sqlbridge --help yields:
usage: sqlbridge [-h] [-w WSOCKET] [-r REALM] [-v] [-u USER] [-s PASSWORD]
             [-e ENGINE] [-d DSN] [-t TOPIC_BASE]

db admin manager for autobahn

optional arguments:
  -h, --help            show this help message and exit
  -w WSOCKET, --websocket WSOCKET
                        web socket ws://127.0.0.1:8080/ws
  -r REALM, --realm REALM
                        connect to websocket using "realm" realm1
  -v, --verbose         Verbose logging for debugging
  -u USER, --user USER  connect to websocket as "user" db
  -s PASSWORD, --secret PASSWORD
                        users "secret" password
  -e ENGINE, --engine ENGINE
                        if specified, a database engine will be attached. Note
                        engine is rooted on --topic
  -d DSN, --dsn DSN     if specified the database in dsn will be connected and
                        ready
  -t TOPIC_BASE, --topic TOPIC_BASE
                        if you specify --dsn then you will need a topic to
                        root it on, the default com.db is fine.
I don't like passing the user and password on the command line, I'll have to get back to that.
```

```sh
python db.py
```

You can fire up the db engine like this, but, it is more useful to use it to fire up your database connections.  For postgres, I would do this:

```
dbengine.py -r dbrealm -u autodb -s autodbsecret -e PG9_4 -t 'com.db' -d 'dbname=autobahn host=ab user=autouser' -v
dbengine.py -r dbrealm -u autodb -s autodbsecret -e MYSQL -t 'com.db' -d 'database=autobahn user=autouser password=123test' -v
dbengine.py -r dbrealm -u autodb -s autodbsecret -e SQLITE -t 'com.db' -d 'dbname=/tmp/autobahn' -v
```

This sets up service for your autobahn router.  The service connects to autobahn using autodb/autodbsecret .  The service is anchored on topic 'com.db' (meaning that all of the calls registered and subscriptions offered will be rooted here, like com.db.query). The postgres database is connected to using the dsn describe by the -d flag. Finally, the -e is the engine, PG9\_4 and MYSQL14\_14 are supported.

Once you have a database engine up and running the following operations are available:

# Basic Documentation

## -t 'topic.base'

All of the actions that can be performed are rooted on the topic base you provided with the -t flag. For example purposes, I will use com.db here, but, this can be any topic you want.

## com.db.connect dsn

Connect to a database.  The dsn is formatted like psycopg2 requires.  There are engine specific arguments, most of which can be seen in the example above.

## com.db.disconnect

Disconnect from a database.

## com.db.query query args

Run query on the database.  Argument substitution with supplied arguments.  Depending on the database the query will look different.  For example, postgres uses the realdictcursor, so inline substitution is done with %(name)s tags. Sqlite3 uses tags that look like :name. The result of the query is an array of dictionary rows.

## com.db.operation query args

Run an operation.  The difference between an operation and a query is that an operation does not expect an answer (like an insert statement).

## com.db.watch name

This function is probably only valid on a postgres database.  Postgres has a notify/listen feature that provides for async notification that something has happened in the database.  This watch function sets up a 'LISTEN' for one of these notifications.  When called, watch will create a new publication rooted on com.db.watch with an arbitrary random name. For example, say I want to know any time the employee data changes.  I do something like: sub\_topic = yield my\_app.call('com.db.watch','employee\_change').  This will return a topic string like com.db.watch.abcdefghij (random lower case characters).  I then subscribe to that.  Anytime a database client issues a NOTIFY employee\_change my subscription will get published with the payload.


