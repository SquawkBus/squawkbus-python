# Authentication & Authorization

Clients must authenticate with the server if the server is given a password
file. Authentication also allows for authorization, which the server may be
configured for.

To authenticate, the client is passed a username and password.

```python
client = await SquawkbusClient.create(host, port, credentials=(username,password))
```

Typically transport layer security would be used to encrypt the credentials.
