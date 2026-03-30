# 1. Use an official Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all your project files (main.py, backend/, frontend/, etc.)
COPY . .

# 5. Tell Google Cloud to use Port 8080 (standard for Cloud Run)
EXPOSE 8080

# 6. Command to start your Streamlit App
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]
