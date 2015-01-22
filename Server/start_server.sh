#!/bin/sh
# Starter opp Serveren.
while [ 1 ]
do
	printf "\e[32mStarting up the server.."
	printf "\e[37m \n"
	python server_heis.py
done

printf "\e[31mError in script. Unable to start the server."
printf "\e[37m \n"