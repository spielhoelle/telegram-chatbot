FROM python:3.9.1
ADD . /python-flask
WORKDIR /python-flask
ENV FLASKAPP=app.py
ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
	PYTHONUNBUFFERED="true"

RUN ls -la
RUN ls -la /python-flask
RUN pip install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]