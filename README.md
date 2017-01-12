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

Open [Merchant Wizard](https://www.blockonomics.co/merchants) and create callback `<gateway domain>/api/v1/callback/?secret=45c75bd587ab4a5b94163c7c741c1dec`

## API

### Create transaction page

request is a POST

```
<gateway domain>/api/v1/transaction/

{
    "token": "...",
    "project_code": "...",
    "amount_usd": 100.00,
    "email": "john@example.com"
}
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

## Callback when transaction changed it's status

It is sent to Site -> Callback url that you configure in /admin/ panel

Request body:

```
{
    "project_code": "...",
    "email": "john@example.com",
    "status": 2,
    "transaction_id": "...."
}
```
