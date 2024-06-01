# Use an official Python runtime as a parent image
FROM python:3.11.5

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install dependencies
ADD pyproject.toml /pyproject.toml
ADD poetry.lock /poetry.lock
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install $(test "$ENVIRONMENT" == prod && echo "--no-dev") --no-root
RUN apt update && apt install -y exiftool

# RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code/
COPY . /code/
