FROM python:3.11-slim

# docker build --tag parcel-track-fetcher:latest --file ./fetcher/Dockerfile ./fetcher
# docker run -it --rm -p 8081:8080/tcp parcel-track-fetcher:latest

WORKDIR /app

COPY src/requirements.txt /app/
RUN python -m pip install -r requirements.txt

COPY src/* /app/

CMD [ "python", "main.py" ]
