FROM python:3.10-alpine
LABEL org-opencontainer.image.authors="jan@macenka.de"
LABEL maintainer="jan@macenka.de"
WORKDIR /code
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:80", "main:app"]