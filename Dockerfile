FROM python:3.10.16-slim

RUN apt-get update && apt-get upgrade -y
# Required for the Docker Client to work within our app inside of another Docker Container
RUN apt-get -y install apt-transport-https ca-certificates curl gnupg2 software-properties-common
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"

COPY . .

RUN pip install -r requirements.txt

WORKDIR /src

CMD ["python", "__main__.py"]