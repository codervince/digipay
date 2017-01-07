# Bitcoins Gateway

- using blockonomics.io for bitocoins processing
- using moneywagon for exchange rates
- coinbase-like design

## Installation

```
pip install -r requirements.txt
make install
make
```

## API

### Create transaction page

request is a POST

```
<gateway domain>?token=<token>&amount_usd=<amount_usd>&project_code=<project_code>&email=<email>
```

response has status code other than 200 and body:

```
{
    "error": "error message"
}
```

response has status code 200 if success and body:

```
{
    "url": "<gateway domain>/<transaction uuid4 id>/"
}
```
