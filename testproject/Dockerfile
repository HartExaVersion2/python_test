FROM python:3.10

# установка библиотек python
RUN pip install --upgrade pip
RUN pip install scrapy

WORKDIR /app

COPY . /app

# run crond as main process of container
CMD scrapy crawl fix_price -O data/results.json