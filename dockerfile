FROM python:3.13-slim

# Set the working directory

WORKDIR /src

# Copy the requirements file into the container at /src

# Copy the current directory

COPY requirements.txt /src

# Install any needed packages specified in requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /src

COPY . /src

# Make port 5001 available

EXPOSE 5001