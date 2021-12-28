clear
echo 
echo
echo
# STOP CONTAINERS
echo "Stopping all Containers..."
docker kill $(docker ps -q)
# DELETE CONTAINERS
echo "Deleting Containers..."
docker rm $(docker ps -aq)
clear
echo
# PRUNE VOLUMES
echo "Pruning orphaned volumes"
docker volume prune -f
echo
echo
echo "Done."
echo
echo



