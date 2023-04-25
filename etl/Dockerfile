FROM python:3.10

WORKDIR /etl

COPY requirements.txt /etl/
COPY ./entrypoint.sh entrypoint.sh

RUN pip install -r requirements.txt --no-cache-dir

COPY . .


RUN chmod +x entrypoint.sh

ENTRYPOINT ["/etl/entrypoint.sh"]