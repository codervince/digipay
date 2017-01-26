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

API key that is added per site is a blockonomics API key. You can find your API key or generate it [here](https://www.blockonomics.co/blockonomics#/settings).

## Deploy & Update

```
ssh dev1@138.68.90.116
update
```

`update` command lives in `/home/dev1/bin/`. Other configs related to server:

- `/etc/nginx/sites-enabled/default`
- `/etc/supervisor.d/conf.d/gateway.conf`

If you put the code into your repository please udpate `update` method and add
new repo to the server repo:

```
cd /home/dev1/gateway
git remote add ...
```

and in `/home/dev1/bin/update` change `git pull --rebase` line with appropriate
repository.

## API

### Create transaction page

request is a POST

```
<gateway domain>/api/v1/transaction/

{
    "token": "...",
    "project_code": "...",
    "amount_btc": 100.00,
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
    "transaction_id": "....",
    "txid": "...."
}
```

## Callback by server initiative

Make `GET` request by: `<gateway domain>/api/v1/transactions/latest/?secret=45c75bd587ab4a5b94163c7c741c1dec` and receive

```
{
    "transactions": [
        {
            "project_code": "...",
            "email": "john@example.com",
            "status": 2,
            "transaction_id": "...",
            "txid": "...",
        },
        ...
    ]
}
```
