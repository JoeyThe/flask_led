#!/bin/bash

cont_name=flask_led
tag=1.0

docker run --device=/dev/ttyACM0:/flask_led/tty --privileged -d -p 5000:5000 --name $cont_name $cont_name:$tag
