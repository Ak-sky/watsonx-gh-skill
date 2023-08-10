FROM python:3.11-alpine

ENV ACCESS_TOKEN=""

WORKDIR /src
COPY . /src

RUN apk add --no-cache vim curl && \
pip install -r requirements.txt --no-cache-dir

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
