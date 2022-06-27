# ip2country Simple Service

This is a simple implementation ip-to-geo service.
It uses generic IPs storage to give the above mapping.
This project currently contains 2 simple implementations: local CSV file and Redis cache.

### API:
1. GET /v1/find-country?ip=\<IPv4 or IPv6\>
   1. On success: 200, `{"country": "XXX", "city":"xxx"}` 
   2. Unknown IP: 200, `{"city": null,"country": null,"message": "IP is unknown"
   3. Bad requests:
      1. 400 on bad IP format
      2. 429 Rate limit
      3. 404/405 Unknown resource.
2. GET /health - Health-check. Use by container orchestration such kubernetes.  

### Adding new IPs DB integration:
1. Implement the `IPsDataStorage` interface.
2. Add your new implementation to the `ip_analyzer.ip_storage.factory.create_storage()` factory. 
3. Set the `DATABASE_TYPE` and `DATABASE_CONF` according to your design.

### IP Rate limiter:
The service limits requests by IP. (i.e the request ip)
This service contains implementation based on the [Sliding-Window](https://www.codementor.io/@arpitbhayani/system-design-sliding-window-based-rate-limiter-157x7sburi#visualizing-sliding-window) algorithm.
It uses two params. Limit (number) and window size in seconds.
For instance, if we set 10 requests as the **limit** and **window size** of 2 sec, it means each user IP cannot be served more than 10 time in a continuous period of 2 seconds.  

### Build locally:
1. Checkout the repository.
2. Run `pip install -r requirements.txt`

### Configuration: 

### IPs database types:
1. LOCAL_TEST - Takes IPs data from file. See: **ips_list.csv**. DO NOT USE IN PRODUCTION.
2. IP_CACHE - Based on Redis. The IPs data should be loaded to Redis in the following format:
    <IP> -> {"country": <COUNTRY>, "city": <CITY> }
    
   1. Configuration for IP_CACHE: `{"host": "<HOST>","port": "<PORT>","password": "<PASS>","db": "<DB>","disable_ssl": "use this key to disable SSL"}`

#### Environment variables:
```sh
SENTRY_DSN = <Sentry dsn key> # Not required 
ENVIRONMENT = <ENV> # default is local
LISTEN_PORT = <PORT> # default is 3001

# DATABASE_TYPE CONF=
DATABASE_TYPE = <> # LOCAL_TEST/IP_CACHE. Default is LOCAL_TEST
DATABASE_CONF = <> # Json configuration for the specific chosen DATABASE_TYPE  

# RATE LIMITER CONF:
LIMITER_REDIS_HOST = <REDIS HOST>
LIMITER_REDIS_PORT = <REDIS PORT>
LIMITER_REDIS_PASS = <REDIS PASS>
LIMITER_REDIS_DB = <REDIS DB>
LIMITER_REDIS_DISABLE_SSL = <Use this env only on loacl dev> # Default is false.
LIMITER_REQ_SEC = <Limit request count for the winddow> # default 10 requests.
LIMITER_WINDOW_SIZE = <Window size in sec> # Default is 3 sec window.
```

### Production Setup:
The service is based on python Flask and should always deploy and run with 
a Web Server Gateway Interface (WSGI).

This project contains a "read-to-use" Dockerfile which build this application with uWSGI application server container and Nginx.

Feel free to deploy this WSGI application with any other WSGI server, but do not use the development server in production! 

#### Tests:
The basic command-line: `python -m unittest discover`

### How to run:
#### Developer service:
Just run app/main.py with the proper environment variables.

#### Run in Docker (using docker compose):
`docker-compose up`

## Enjoy