# Setup
Create environment variables, or put your config into ~/.config/humio/.env
```
HUMIO_BASE_URL=https://xxxxxxxxxxxxxxxxxxxxxxxxxx
HUMIO_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUMIO_QUERY_1_XXX='"request_type" = "xxxxxxxxxx"'
HUMIO_QUERY_1_XXX_REPOSITORY='xxxxxx'
HUMIO_QUERY_1_XXX_SPAN='-60m'
HUMIO_QUERY_1_XXX_INTERVAL_SECONDS=10
HUMIO_QUERY_1_XXX_COLOR=255,255,255,255 # red, green, blue, white
```

Install requirements / Setup virtualenv:
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

./numbersboard.py
or
./numbersboard.py --help

```

# Hardware
RaspberryPi v4, with hardware as described [here](https://github.com/agjendem/rpi-7segment)

## 7-segment:
* Library: [rpi-7segment](https://github.com/agjendem/rpi-7segment)
* Runs on external 12v power supply.

## Led-strips:
* Library: [rpi_ws281x](https://github.com/jgarff/rpi_ws281x)
* Guide: https://dordnung.de/raspberrypi-ledstrip/ws2812
* Runs on external 5v power supply.
