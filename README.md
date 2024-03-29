
# ----------------------------------------------------
# MOVED TO https://github.com/tapis-project/tokens-api 
# ----------------------------------------------------

# Tapis Tokens API

REST API and OAuth2 server for working with authentication tokens for the Tapis v3 Platform.

## Usage
This repository includes build files and other assets needed to start the service locally. Clone this
repository and follow the steps in the subsequent section.

### Start the API Locally
We are automating the management of the lifecycle workflow with `make`. You will need to install `make` it in order
to use the steps bellow.

The make system is generic and used by multiple Tapis services. Before following any of the sections below,
be sure to

```
$ export API_NAME=tokens
```

The `API_NAME` variable is used to let the `make` system know which Tapis service to work with.


#### First Time Setup
Starting the API the first time requires some initial setup. Do the following steps once per machine:

1. `make init_dbs` - creates a new docker volume, `tokens-api_pgdata`, creates a new Postrgres
Docker container with the volume created, and creates the initial (empty) database and database user.
2. `make migrate.upgrade` - runs the migrations contained within the `migrations/versions` directory.
3. `docker-compose up -d tokens` - starts the Tokens API.

#### Updating the API After the First Setup
Once the First Time Setup has been done a machine, updates can be fetched applied as follows:

1. `git pull` - Download the latest updates locally.
2. `make build.api` - Build a new version of the API container image.
3. `make migrate.upgade` - Run any new migrations (this step is only needed if new files appear in the `versions`
directory).migrations
4. `docker-compose up -d tokens` - start a new version of the Tokens API.

#### New DB Schema
During initial development, the database schema can be in flux. Changes to the models require new migrations. Instead of
adding additional migration versions, the database and associated `migrations` directory can be "wiped" and recreated
from the new models code using the following steps:

1. `make wipe` - removes the database and API container, database volume, and the `migrations` directory.database
2. `make init_dbs` - creates a new docker volume, `tenant-api_pgdata`, creates a new Postrgres
Docker container with the volume created, and creates the initial (empty) database and database user.
3. Add the migrations:

```
docker run -it --rm --entrypoint=bash --network=tokens-api_tokens -v $(pwd):/home/tapis/mig tapis/tokens-api
  # inside the container:
  $ cd mig; flask db init
  $ flask db migrate
  $ flask db upgrade
  $ exit
```

### Quickstart
Use any HTTP client to interact with the running API. The following examples use `curl`.

#### Generate Tokens

Generate an access token:

```
$ curl -H "Content-type: application/json" -d '{"token_tenant_id": "dev", "token_type": "service", "token_username": "jstubbs"}'  localhost:5001/tokens
{
  "message": "Token generation successful.",
  "result": {
    "access_token": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi5hcGkudGFwaXMuaW8vdG9rZW5zL3YzIiwic3ViIjoiZGV2QGpzdHViYnMiLCJ0ZW5hbnRfaWQiOiJkZXYiLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZGVsZWdhdGlvbiI6ZmFsc2UsInVzZXJuYW1lIjoianN0dWJicyIsImFjY291bnRfdHlwZSI6InNlcnZpY2UiLCJleHAiOjE1Njg0MTcxODh9.JBTEK81Uvb1FNRFRm6oLt2Fog3OHmJa9Z4kkRAo7LQlYSbZZdHxXnzTtCXXTrYr7YFIHTQ8xcNLRjwT5nUOaLlmu8qzrjanRbC1XQHZa4jRUOK2ARBUZRK9yVaf2uvbBRJLW_Krzo90p3Pn-RWR2TwcYKtRAQlygKgXdkn1zmZw",
      "expires_at": "2019-09-13 23:26:28.196173",
      "expires_in": 300
    }
  },
  "status": "success",
  "version": "dev"
}

```

Generate access and refresh tokens:

```
$ curl -H "Content-type: application/json" -d '{"token_tenant_id": "dev", "token_type": "service", "token_username": "jstubbs", "generate_refresh_token": true}'  localhost:5001/tokens

{
  "message": "Token generation successful.",
  "result": {
    "access_token": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi5hcGkudGFwaXMuaW8vdG9rZW5zL3YzIiwic3ViIjoiZGV2QGpzdHViYnMiLCJ0ZW5hbnRfaWQiOiJkZXYiLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZGVsZWdhdGlvbiI6ZmFsc2UsInVzZXJuYW1lIjoianN0dWJicyIsImFjY291bnRfdHlwZSI6InNlcnZpY2UiLCJleHAiOjE1Njg0MTcwNDR9.ZE_JqYRhpkAIyExgKP7YAIEIFNROJ4oft0G_dX1Q4WlPmCio2OQ4ajcxEjbfMUgPaFVBIgZ0IOQ76xaWIqtjVyoecCzJDX6U6RLEa-etnJzgfi3D6yjOCYahoAPiLwrCswgVqyGediEAxTvdWQUqK6xsrwiTB7iYT_HRDR_yb8Q",
      "expires_at": "2019-09-13 23:24:04.758644",
      "expires_in": 300
    },
    "refresh_token": {
      "expires_at": "2019-09-13 23:29:04.896390",
      "expires_in": 600,
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi5hcGkudGFwaXMuaW8vdG9rZW5zL3YzIiwic3ViIjoiZGV2QGpzdHViYnMiLCJ0ZW5hbnRfaWQiOiJkZXYiLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsInVzZXJuYW1lIjoianN0dWJicyIsImFjY291bnRfdHlwZSI6InNlcnZpY2UiLCJleHAiOjE1Njg0MTczNDQsImFjY2Vzc190b2tlbiI6eyJpc3MiOiJodHRwczovL2Rldi5hcGkudGFwaXMuaW8vdG9rZW5zL3YzIiwic3ViIjoiZGV2QGpzdHViYnMiLCJ0ZW5hbnRfaWQiOiJkZXYiLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZGVsZWdhdGlvbiI6ZmFsc2UsInVzZXJuYW1lIjoianN0dWJicyIsImFjY291bnRfdHlwZSI6InNlcnZpY2UifX0.rdCY7xGTIyMa04AtxIKeBCV06i0dI4kJC0R-uZQwRC6GIH2sNE9qc7YPE5qYTPpAWneuMd-pMc7SijW2DPkIQdGQOuVHd_m-L5aivVmyfh9IR69x2rx5RXFo5iLEDtz-9eBFw81JTXYpNc-W2mIYeTwQTijt_KbibwWa7Nvj2xw"
    }
  },
  "status": "success",
  "version": "dev"
}
```

Use a refresh token to get a new access and refresh token pair:

```
$ curl -X PUT  -H "Content-type: application/json" -d '{"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi5hcGkudGFwaXMuaW8vdG9rZW5zL3YzIiwic3ViIjoiZGV2QGpzdHViYnMiLCJ0ZW5hbnRfaWQiOiJkZXYiLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU2ODQ4NjIxMywiYWNjZXNzX3Rva2VuIjp7ImlzcyI6Imh0dHBzOi8vZGV2LmFwaS50YXBpcy5pby90b2tlbnMvdjMiLCJzdWIiOiJkZXZAanN0dWJicyIsInRlbmFudF9pZCI6ImRldiIsInRva2VuX3R5cGUiOiJhY2Nlc3MiLCJkZWxlZ2F0aW9uIjpmYWxzZSwidXNlcm5hbWUiOiJqc3R1YmJzIiwiYWNjb3VudF90eXBlIjoic2VydmljZSIsInR0bCI6MzAwfX0.d6L2s6uLidgsSpnoDsRB2qKJhpiK7moUX6Hd-wAZnms7BvT7uFfq5Pjx6EzChTXSyJYICtLVhOppkDjRKAQI3Rv6HyU3HMKC25r1_hRHLOmCzA2OK3G8Zm8cMAW8iAiamRCriocdxqnWignmDiuRmTGyhLeb2RGtYccX_yz3Hbw"}'  localhost:5001/tokens

{
  "message": "Token generation successful.",
  "result": {
    "access_token": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi5hcGkudGFwaXMuaW8vdG9rZW5zL3YzIiwic3ViIjoiZGV2QGpzdHViYnMiLCJ0ZW5hbnRfaWQiOiJkZXYiLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZGVsZWdhdGlvbiI6ZmFsc2UsInVzZXJuYW1lIjoianN0dWJicyIsImFjY291bnRfdHlwZSI6InNlcnZpY2UiLCJleHAiOjE1Njg0ODYzMDN9.KBChtfKzuMqgQimFEkrSuc8XZHjStlsB8V6VnbKcIk_uIGTvXYI6rHY8KEC_b8DCaqP6Wm8eDslN4TP5O9XWkqTAG_ZMmk4VIFZNJFFyUcGth5eYdxuiFcDoRqd79zgVrrdp-ghvRrUl8EBOOV6HIkVsVhMTcgsI1TRO44RxiYk",
      "expires_at": "2019-09-14 18:38:23.513697",
      "expires_in": 300
    },
    "refres_token": {
      "expires_at": "2019-09-14 18:43:23.514270",
      "expires_in": 600,
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Rldi5hcGkudGFwaXMuaW8vdG9rZW5zL3YzIiwic3ViIjoiZGV2QGpzdHViYnMiLCJ0ZW5hbnRfaWQiOiJkZXYiLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU2ODQ4NjYwMywiYWNjZXNzX3Rva2VuIjp7ImlzcyI6Imh0dHBzOi8vZGV2LmFwaS50YXBpcy5pby90b2tlbnMvdjMiLCJzdWIiOiJkZXZAanN0dWJicyIsInRlbmFudF9pZCI6ImRldiIsInRva2VuX3R5cGUiOiJhY2Nlc3MiLCJkZWxlZ2F0aW9uIjpmYWxzZSwidXNlcm5hbWUiOiJqc3R1YmJzIiwiYWNjb3VudF90eXBlIjoic2VydmljZSIsInR0bCI6MzAwfX0.TWcAX0N9UpNqvjAMsoAvURL-jIWJFLsnzkrzGdB3ypUumD-5XyiFyLdZeIqZeMfk9wtq8cVj0OS0upxY5jwJ_XTWz0BCRkMDPoya1zeaDW9FOsVwt91Y44aB8u9KzNf7hywd5tI3kikwUAGi0FsJXuvpkkwAzM1mk3I8plX8uQM"
    }
  },
  "status": "success",
  "version": "dev"
}

```

### Key Format and Generating a Public/Private Key Pair
(TODO - needs more detail)

The format of the public and private keys must be exact. Specifically, the `-----BEGIN RSA PRIVATE KEY-----\n`
and `-----END RSA PRIVATE KEY-----\n` must be included in the private key
and the `-----BEGIN RSA PUBLIC KEY-----\n` and `-----END RSA PUBLIC KEY-----\n` must
be included in the public key. 

For local development, generate a public/private RSA256 key pair with the following commands:

First, generate a private key and write it to a file -  
```
$ private_key=`openssl genrsa 1024`
$ echo $private_key > private.key
```

Extract the public key to a file:
```
echo "$private_key" | sed -e 's/^[ ]*//' | openssl rsa -pubout  > key.pub
```

Make sure to remove any spaces and covert line breaks to new line characters (`\n`)
in both the public and private key strings in the files. Them copy the strings
to the corresponding service config files, as necessary.
