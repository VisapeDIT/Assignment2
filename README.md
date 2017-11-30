# Assignment2

1. Create the image: docker build -t <tag> .

# Run as a container
2. Run a container: docker run --privileged -d -p 80:5000 --name <container-name> -v /var/run/docker.sock:/var/run/docker.sock <image>

# Run as a service
2. docker service create --replicas 3 -d -p 80:5000 --name web --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock <image>
