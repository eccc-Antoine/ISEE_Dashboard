# Use a lightweight official Python base image
FROM python:3.11.5

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the repo (your Streamlit app)
COPY . .

# Expose Streamlit’s default port
EXPOSE 443

# Streamlit environment variables
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=443
ENV STREAMLIT_SERVER_ENABLECORS=false

HEALTHCHECK CMD curl --fail http://localhost:443/_stcore/health

# Run the Streamlit app
CMD ["streamlit", "run", "DASHBOARDS/ISEE/Home_🏠.py", "--server.port=443", "--server.address=0.0.0.0"]