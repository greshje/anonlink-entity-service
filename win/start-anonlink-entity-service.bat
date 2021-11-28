@echo off
echo.
echo.
echo Starting anonlink entity service (aes)...
echo.
echo.
docker-compose -p anonlink -f ../tools/docker-compose.yml up --remove-orphans


