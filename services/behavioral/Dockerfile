FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/interviewers /app/interviewers

EXPOSE 50053

CMD ["python", "-m", "interviewers.services.behavioral"]
