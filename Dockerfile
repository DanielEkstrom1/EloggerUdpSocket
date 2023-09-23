FROM python:3.11.4-slim-bullseye

RUN pip install --upgrade pip

WORKDIR /app

COPY app .

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python3","-u" ,"udpsocket.py"]