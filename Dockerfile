FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get upgrade -y

COPY . .
RUN pip install -r requirements.txt

WORKDIR /src
EXPOSE 8000
CMD ["fastapi", "run", "main.py"]