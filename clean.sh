#!/bin/bash

cont_name=flask_led
tag=1.0

docker stop $cont_name
docker remove $cont_name
docker rmi $cont_name:$tag
