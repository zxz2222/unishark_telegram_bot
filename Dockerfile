# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for the port
ENV PORT 8000

# Run bot.py when the container launches
# Use gunicorn as the production web server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bot:app"]
