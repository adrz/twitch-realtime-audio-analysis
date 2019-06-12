FROM frolvlad/alpine-python3:latest

WORKDIR /app
COPY requirements.txt app.py wsgi.py ./
COPY src src

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENTRYPOINT ["gunicorn", \
	   "--workers", "4", \
	   "--bind", "0.0.0.0:8283", \
	   "wsgi"]

EXPOSE 8283
