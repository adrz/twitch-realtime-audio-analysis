# Docker

```bash
docker-compose -f docker-compose.yml up --build --scale consumer=2
```

# Hostnames

```bash
apk add --update --no-cache bind-tools
host -t A consumer|grep -E -o '[0-9]+\.[0-9]+\.[0-9]\.[0-9]+'|awk {'print'} ORS=','
```
