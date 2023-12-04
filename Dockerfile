# Use a base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the project files to the working directory
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose a port (if needed)
EXPOSE 8000

# Define environment variables (if needed)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Define the command to run the application
CMD ["flask", "run", "--port=8000"]
