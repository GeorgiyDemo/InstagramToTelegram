FROM ubuntu:18.04

RUN apt-get update && apt-get install wget gnupg2 -y
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

RUN apt-get install -yqq unzip
# Версия драйвера 75.0.3770.90, можно изменить тут
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/75.0.3770.90/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

ENV DISPLAY=:99

ENV LANG="en_US.UTF-8"
RUN apt-get install -y locales
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    /usr/sbin/update-locale LANG=en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV PATH="${PATH}:/usr/local/bin/"

RUN \
  apt-get update && \
  apt-get install -y python3 python3-pip python3-dev
RUN apt-get install tesseract-ocr libsm6 libxext6 -y
WORKDIR /root/
ADD . /root/

RUN mv eng.traineddata /usr/share/tesseract-ocr/4.00/tessdata/
RUN pip3 install -r requirements.txt

CMD python3 start.py