# Use an official Python image
FROM python:3.12

# Install FFmpeg
RUN apt update && apt install -y ffmpeg

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the correct port for Railway
EXPOSE 5000

# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
