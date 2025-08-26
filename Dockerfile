FROM python:3.10-slim

# SET ENVIRONMENT VARIABLES
ENV PYTHONUNBUFFERED = 1
ENV PYTHONDONTWRITEBYTECODE = 1

# SET WORKING DIRECTORY
WORKDIR /app

# INSTALL DEPENDENCIES
RUN apt-get update && apt-get install -y build-essential poppler-utils && rm -rf /var/lib/apt/lists/*

# COPY REQUIREMENTS
COPY requirements.txt .
COPY .env .

# COPY PROJECT PLAN
COPY . .

# INSTALL DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE PORT
EXPOSE 8000

# RUN SERVER
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# PRODUCTION ENVIRONMENT
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]