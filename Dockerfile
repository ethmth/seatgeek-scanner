FROM debian:11

RUN apt update && apt upgrade -y
RUN apt install python3 python3-pip firefox-esr wget -y

RUN pip install --upgrade pip
RUN pip install selenium requests python-dotenv

RUN cd /tmp
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz
RUN tar -xvf geckodriver-v0.31.0-linux64.tar.gz
RUN mv geckodriver /usr/local/bin
RUN chmod +x /usr/local/bin/geckodriver

COPY ./src/ /opt/src

WORKDIR /opt/src

ENTRYPOINT ["python3","browser.py"]
CMD [""]
