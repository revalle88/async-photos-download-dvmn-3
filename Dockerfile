FROM python:3.9

COPY requirements.txt .

RUN apt-get update && apt-get install -y zip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "server.py" ]