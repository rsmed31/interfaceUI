# Use a minimal Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy the project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for the app
EXPOSE 8000

# Run the application
CMD ["python", "src/app.py"]
