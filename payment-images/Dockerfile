FROM python:3.9

WORKDIR /app

# Install system dependencies for python-magic
RUN apt-get update && apt-get install -y libmagic1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]