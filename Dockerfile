FROM python:3.9.1
ADD . /python-flask
WORKDIR /python-flask
ENV FLASKAPP=app.py
ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
	PYTHONUNBUFFERED="true"

RUN pip3  install tensorflow  --no-cache-dir
RUN pip install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]