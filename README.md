# Parcel Track

Ongoing project to simplify the tracking of my orders.

## Fetcher

The `parcel-track-fetcher` container offers a REST API, to get a full documentation check the doc comments or run the container and open the Swagger UI at [http://localhost:8080/](http://localhost:8080/).

Configure the timezone of the dates in responses via the optional `OUTPUT_TZ` environment variable, default is UTC.

```bash
docker run -it --rm -p 8080:80/tcp -e OUTPUT_TZ=Europe/Berlin ghcr.io/hasehh/parcel-track-fetcher:main
```

> **Disclaimer:** The `fetcher` gets the data directly from the parcel carriers, meaning every call you make is a call on their infrastructure.
> Making too many requests can lead to you being blocked or otherwise questioned, please be respectful in your usage.
> Also, don't host the service publicly without any authentication or similar to prevent abuse through third parties.
> I do not take responsibility for any consequences that arise for you from using this project, as is stated in the license.
