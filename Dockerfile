# Dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the Python path environment variable
ENV PYTHONPATH=/app

# Pass environment variables during build
ARG CLICKUP_API_KEY
ARG CLICKUP_LIST_ID
ARG SCORES_FIELD_ID
ARG PLOT_FIELD_ID
ARG ANSWERS_FIELD_ID
ARG ROUTINES_FIELD_ID
ARG TYPEFORM_API_KEY
ARG FORM_ID

# Set environment variables at runtime
ENV CLICKUP_API_KEY=$CLICKUP_API_KEY
ENV CLICKUP_LIST_ID=$CLICKUP_LIST_ID
ENV SCORES_FIELD_ID=$SCORES_FIELD_ID
ENV PLOT_FIELD_ID=$PLOT_FIELD_ID
ENV ANSWERS_FIELD_ID=$ANSWERS_FIELD_ID
ENV ROUTINES_FIELD_ID=$ROUTINES_FIELD_ID
ENV TYPEFORM_API_KEY=$TYPEFORM_API_KEY
ENV FORM_ID=$FORM_ID

# Copy the rest of the application code into the container
COPY . .

# Expose the necessary port
EXPOSE 80

# Specify the command to run the Flask app
CMD ["python", "main_flask.py"]
