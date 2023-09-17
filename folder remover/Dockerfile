FROM continuumio/anaconda3

RUN apt update
RUN apt -y upgrade
RUN conda update conda

# linux dependancies
RUN apt -y install fonts-ipaexfont

# pip dependancies
RUN pip install jpholiday

# conda dependancies, if needed

RUN apt autoremove -y
RUN apt clean -y

# 実行ディレクトリの指定
WORKDIR /project_dir