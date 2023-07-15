FROM python:3.10

EXPOSE 80

WORKDIR /src
COPY requirements.txt /src
RUN pip install -r requirements.txt

COPY . /src

CMD ["python", "src/main.py"]

