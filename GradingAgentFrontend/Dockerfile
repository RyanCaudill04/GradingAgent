FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN python3 manage.py collectstatic --noinput
CMD ["gunicorn", "web.wsgi", "--bind", "0.0.0.0:8000"]
