COMP90020 Distributed Algorithms project
Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901\

------------------------------------------------------------------
changed files:
/capture.py
/game.py
/logger.py
/socReceiver.py
/gameController/*
/networking/*
/video/*
/image/*
------------------------------------------------------------------
system requirements:
linux/mac preferred
python 2.7.16
python-tk
keyboard
------------------------------------------------------------------
commands (4 nodes)
> python capture.py --ip 127.0.0.1 --port 8000 --soc0 --soc1 --soc2 --soc3 --keys0
> python capture.py --ip 127.0.0.1 --port 8001 --soc0 --soc1 --soc2 --soc3 --keys1
> python capture.py --ip 127.0.0.1 --port 8002 --soc0 --soc1 --soc2 --soc3 --keys2
> python capture.py --ip 127.0.0.1 --port 8003 --soc0 --soc1 --soc2 --soc3 --keys3
------------------------------------------------------------------
in-game commands (on 127.0.0.1 8000)
> connect 127.0.0.1 8001
> connect 127.0.0.1 8002
> connect 127.0.0.1 8003
> gamestart
