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
EXPOSE 8501

# Streamlit environment variables
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLECORS=false

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the Streamlit app
CMD ["streamlit", "run", "DASHBOARDS/ISEE/ISEE_FULL_DUCK.py", "--server.port=8501", "--server.address=0.0.0.0"]