@echo off
echo.
echo.
echo Starting anonlink entity service (aes)...
echo.
echo.
docker-compose -p anonlink -f ../tools/docker-compose.yml up --remove-orphans
:: docker-compose -p anonlink -f ../anonlink-entity-service/tools/docker-compose.yml up --scale backend=8 --remove-orphans

