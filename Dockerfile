FROM python:3.10-buster

RUN apt-get update && apt-get upgrade -y

COPY . .

RUN pip install -r requirements.txt

WORKDIR /src

CMD ["python", "src/__main__.py"]