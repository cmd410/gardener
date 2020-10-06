FROM python:3.8.6-alpine3.11
WORKDIR /src/
COPY . /src/
RUN apk add --no-cache python3-dev libffi-dev gcc musl-dev make nodejs npm
RUN pip install -r requirements.txt
RUN npm install -g insect
ENTRYPOINT ["python"]
CMD ["main.py"]
