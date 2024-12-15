# SSL

Transport layer security (TLS or historically SSL) can be used to
encrypt the data sent between the client and the server. This is
useful if the data is private, or when passwords are exchanged.

## Overview

To connect a client over using transport layer security
pass the `ssl` argument to the client `create` class method.

The argument can be one of the following:

* True - Use the default SSL client context. This is almost always what you want.
* Path to a bundle - Useful for self signed certificates.
* A pre-built SSLContext - For total control over the SSL context.
* None or False - No do not use tls.

### No TLS

If TLS is not required, pass `None` for the `ssl` argument.

```python
client = await SquawkbusClient.create('localhost', 8553, ssl=None)
```

Or just omit it.

```python
client = await SquawkbusClient.create('localhost', 8553, ssl=None)
```

### Default TLS

If you want TLS the most simple way is to pass `True` to the `ssl` argument.

Note: You **must** use the actual fully qualified domain name (like `"host.example.com"`),
because this is how the client verifies the identity of the server.

```python
client = await SquawkbusClient.create('host.example.com', 8553, ssl=True)
```

### Self Signed Certificates

For testing, self-signed certificates can be used.
See [here](https://github.com/rob-blackbourn/ssl-certs) for how to create them.

For the client to verify self signed certificates a bundle can be provided. If
article above is used the bundle can be built in the following way.

```bash
cat intermediate-ca.pem root-ca.pem > /tmp/cacerts.pem
```

```python
client = await SquawkbusClient.create(
    'host.example.com',
    8553,
    ssl="/tmp/cacerts.pem"
)
```

### Custom Contexts

For total control an `ssl.SSLContext` can be passed.

```python
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

client = await SquawkbusClient.create(
    'host.example.com',
    8553,
    ssl=context
)
```
