FROM python:3.12-slim

ENV OUTPUT_TZ "UTC"
ENV DEVELOPMENT "False"

WORKDIR /app
COPY src/* /app/
RUN python -m pip install -r requirements.txt

CMD [ "python", "main.py" ]
