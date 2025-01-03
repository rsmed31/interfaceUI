# Use a minimal Python base image
FROM python:3.12-alpine

# Set working directory inside the container
WORKDIR /app

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose the port for the app
EXPOSE 8050

# Run the application
CMD ["python", "src/app.py"]