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
# CREATE LOG DIR
mkdir ./logs
# DELETE OLD FULL LOG FILE
echo "Deleting old full log file..."
touch ./logs/full-log.txt
rm ./logs/full-log.txt
touch ./logs/full-log.txt
# SET UP LRP LOG FILE
echo "Deleting old lrp log file..."
touch ./logs/lrp-log.txt
rm ./logs/lrp-log.txt
touch ./logs/lrp-log.txt 
# TAIL THE FULL LOG FILE (display the running process in a cygwin window)
cygstart tail -f ./logs/full-log.txt
# WRITE THE LONG RUNNING PROCESS LOG
echo "Starting LRP log..." 
( tail -f ./logs/full-log.txt | grep --line-buffered "LOG_FILE:" > ./logs/lrp-log.txt; ) &
echo "Starting tail of ./logs/lrp-log.txt"
cygstart tail -f ./logs/lrp-log.txt
# START AES
echo "Starting anonlink entity service (aes)..."
echo "Process is running and writing log to ./full-log.txt"
echo "Long Running Process Log (LRP) is being written to lrp-log.txt"
echo
echo "! ! !"
echo "! ! ! DO NOT CLOSE THIS WINDOW ! ! !"
echo "! ! !"
echo
echo "(<ctrl-c> to quit the process)"
docker-compose -p anonlink -f ../tools/docker-compose.yml up --remove-orphans > ./logs/full-log.txt
echo
echo
echo "Done."
echo
echo



