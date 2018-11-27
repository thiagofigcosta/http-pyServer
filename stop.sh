#!/bin/bash
kill -SIGINT $(ps aux | grep '[p]ython Server.py' | awk '{print $2}')
