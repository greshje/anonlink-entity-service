@echo off
echo.
echo.
echo Deleting Containers...
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker rm %%i
echo.
echo Pruning orphaned volumes
docker volume prune -f
echo.
echo Starting anonlink entity service (aes)...
docker-compose -p anonlink -f ../tools/docker-compose.yml up --remove-orphans
echo.
echo.
echo Done.
echo.
echo.


