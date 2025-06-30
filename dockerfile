# Use official Python base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy dependencies list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files to container
COPY . .

# Expose port (Flask default)
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Start the Flask app
CMD ["flask", "run"]