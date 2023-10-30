FROM python:3.12-slim

# docker build --tag parcel-track-fetcher:latest --file ./fetcher/Dockerfile ./fetcher
# docker run -it --rm -p 8081:80/tcp --mount type=bind,source="$(pwd)"/fetcher/src,target=/app parcel-track-fetcher:latest

WORKDIR /app
COPY src/* /app/
RUN python -m pip install -r requirements.txt

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload" ]
