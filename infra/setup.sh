# deploy swarm
docker stack deploy -c docker-compose.yaml order

# delete swarm
docker stack rm order