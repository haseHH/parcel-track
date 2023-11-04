# Parcel Track

Ongoing project to simplify the tracking of my orders.

## Fetcher

The `parcel-track-fetcher` container offers a REST API, to get a full documentation check the doc comments or run the container and open the Swagger UI at [http://localhost:8080/](http://localhost:8080/).

Configure the timezone of the dates in responses via the optional `OUTPUT_TZ` environment variable, default is UTC.

```bash
docker run -it --rm -p 8080:80/tcp -e OUTPUT_TZ=Europe/Berlin ghcr.io/hasehh/parcel-track-fetcher:main
```
