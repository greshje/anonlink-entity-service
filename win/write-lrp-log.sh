clear
echo 
echo
echo "Starting tail..."
tail -f ./logs/full-log.txt | grep --line-buffered "LOG_FILE:" > ./logs/lrp-log.txt

