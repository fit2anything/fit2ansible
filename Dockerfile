FROM registry.fit2cloud.com/public/python:v3
MAINTAINER Fit2Ansible Team <support@fit2cloud.com>
WORKDIR /opt/fit2ansible

COPY ./requirements /tmp/requirements
RUN cd /tmp/requirements && yum -y install epel-release && \
    echo -e "[mysql]\nname=mysql\nbaseurl=https://mirrors.tuna.tsinghua.edu.cn/mysql/yum/mysql57-community-el6/\ngpgcheck=0\nenabled=1" > /etc/yum.repos.d/mysql.repo && \
    yum -y install $(cat rpm_requirements.txt)
RUN cd /tmp/requirements && \
     pip install --upgrade pip setuptools -i https://mirrors.aliyun.com/pypi/simple/ && \
     pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ || pip install -r requirements.txt
RUN sed -i "s@'uri': True@'uri': False@g" /usr/local/lib/python3.6/site-packages/django/db/backends/sqlite3/base.py
RUN test -f /root/.ssh/id_rsa || ssh-keygen -f /root/.ssh/id_rsa -t rsa -P ''
RUN echo -e "Host *\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile /dev/null" > /root/.ssh/config

COPY . /opt/fit2ansible
VOLUME /opt/fit2ansible/data
RUN echo > config.yml

ENV LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8
ENV PYTHONOPTIMIZE=1
ENV C_FORCE_ROOT=1
ENV SECRET_KEY=PleasgeChangeMeForSafety
ENV DEBUG=false
ENV DB_ENGINE=sqlite3
ENV DB_NAME=sqlite3.db

EXPOSE 8000
EXPOSE 8001
ENTRYPOINT ["./entrypoint.sh"]
