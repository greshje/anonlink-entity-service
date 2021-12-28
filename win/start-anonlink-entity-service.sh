echo 
echo
echo
# STOP CONTAINERS
echo "Stopping all Containers..."
docker kill $(docker ps -q)
# DELETE CONTAINERS
echo "Deleting Containers..."
docker rm $(docker ps -aq)
echo
# PRUNE VOLUMES
echo "Pruning orphaned volumes"
docker volume prune -f
echo
# DELETE OLD FULL LOG FILE
echo "Deleting old full log file..."
touch full-log.txt
rm full-log.txt
touch full-log.txt
# DELETE THE LRP LOG FILE
echo "Deleting old lrp log file..."
touch lrp-log.txt
rm lrp-log.txt
touch lrp-log.txt
# TAIL THE LOG FILE (display the running process in a cygwin window)
# cygstart tail -f full-log.txt
# cygstart tail -f lrp-log.txt
# WRITE LOG_FILE LINES TO THE LRP LOG_FILE
# cygstart tail -f full-log.txt | grep "LOG_FILE:" > lrp-log.txt
# START AES
echo "Starting anonlink entity service (aes)..."
echo "Process is running and writing log to ./full-log.txt"
echo "Long Running Process Log (LRP) is being written to lrp-log.txt"
echo "! ! ! DO NOT CLOSE THIS WINDOW ! ! !"
echo "(<ctrl-c> to quit the process)"
docker-compose -p anonlink -f ../tools/docker-compose.yml up --remove-orphans > full-log.txt
echo
echo
echo "Done."
echo
echo



