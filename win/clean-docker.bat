@echo off
echo.
echo.
:: STOP CONTAINERS
echo Stopping all Containers...
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker kill -f %%i
:: DELETE CONTAINERS
echo Deleting Containers...
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker rm -f %%i
echo.
:: PRUNE VOLUMES
echo Pruning orphaned volumes
docker volume prune -f
echo.
:: DELETE IMAGES
echo Deleting Images...
:: for /F %i in ('docker images -a -q') do docker rmi -f %i
FOR /f "tokens=*" %%i IN ('docker images -a -q') DO docker rmi -f %%i
echo.
echo.
echo Done.
echo.
echo.

