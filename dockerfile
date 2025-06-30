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

# Expose port (Gunicorn default port is 8000, but Railway/Render often use 5000)
EXPOSE 5000

# Set environment variables
ENV PORT=5000

# Start app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
