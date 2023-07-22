docker-compose rm -f

# Build the Docker image
docker build . -t flaskapp:test 

# Run the Docker container
docker-compose up --force-recreate