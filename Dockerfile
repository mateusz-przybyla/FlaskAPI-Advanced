FROM python:3.13
EXPOSE 5000
WORKDIR /app
COPY requirements.txt requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . . 
CMD ["flask", "run", "--host", "0.0.0.0"]