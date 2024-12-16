# Simple examples

This folder contains some basic examples.

The examples expect a squawkbus server to be running on the local machine
on the default port, without authentication or TLS. The server can be launched
in the following way.

```bash
squawkbus
```

It can be useful to get more logging out of the server.

```bash
LOGGER_LEVEL_SQUAWKBUS=DEBUG squawkbus
```

After starting the server, startup the notifier, and choose a topic pattern
that will be used later on, for example `F.*`.

```
Topic pattern: F.*
```

Next, startup the subscriber. Enter a topic that would match the pattern used for
the notifier, for example `FOO`.

```
Topic: FOO
```

The notifier should report that a client has subscribed to `FOO`.

Finally start the publisher. Enter the message for the topic as follows:

```
Topic: FOO
Entitlement: 0
Content type (text/plain): text/plain
Data: Hello, World!
Entitlement: <ENTER>
```

(An empty entitlement ends the message).

The subscriber should report the message.