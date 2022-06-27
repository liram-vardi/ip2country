# ip2country simple service


#### Tests:
The basic command-line: `python -m unittest discover`



##### Run local Redis:
1) `docker run --name my-redis -e REDIS_PASSWORD="pass" -p 6379:6379 -d redis /bin/sh -c 'redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}'`
