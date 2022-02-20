FROM python:3.9-alpine
LABEL maintainer="Evian <Evian#6930>"

LABEL build_date="2022-02-19"
RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers
WORKDIR /dc_speedashing_bot
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "index.py"]
