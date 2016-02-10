# weather-station-reader
Personal RasPi weather station code so I don't forget how to set stuff up again

## You forgot again didn't you...

Install stuff:

    sudo apt-get install build-essential python-dev

Get and install the Adafruit DHT library:

    git clone https://github.com/adafruit/Adafruit_Python_DHT.git
    cd Adafruit_Python_DHT/
    python setup.py install

Download python-mysql-connector:

    http://dev.mysql.com/downloads/connector/python/

A freaking database (MySQL, Google for help)

    CREATE USER whoever IDENTIFIED BY password;
    GRANT PRIVILEGE ...

    CREATE DATABASE wstation;
    USE wstation;

    CREATE TABLE readings (
        id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
        temperature DECIMAL(5,2),
        humidity DECIMAL(5,2),
        illuminence DECIMAL(8,2),
        timestamp TIMESTAMP DEFAULT NOW()
    );

## Running on cron
Edit your root crontab:

    sudo crontab -e

Time it every 15 minutes:

    */15 * * * * python /path/to/getReadings.py

