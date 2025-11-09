FROM python:3.11-slim

# Install Node.js + npm + npx
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g vercel

# Work inside app folder
WORKDIR /app

# Copy app code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Start server
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

