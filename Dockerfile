FROM registry.fit2cloud.com/public/python:v3
MAINTAINER Fit2Openshift Team <support@fit2cloud.com>
WORKDIR /opt/fit2openshift

RUN echo -e '[mysql]\nname = mysql\nbaseurl = http://mirrors.ustc.edu.cn/mysql-repo/yum/mysql-5.7-community/el/6/$basearch/\ngpgcheck = 0' > /etc/yum.repos.d/mysql.repo
COPY ./requirements /tmp/requirements
RUN cd /tmp/requirements && yum -y install epel-release && yum -y install $(cat rpm_requirements.txt)
RUN cd /tmp/requirements && \
     pip install --upgrade pip setuptools -i https://mirrors.aliyun.com/pypi/simple/ && \
     pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ || pip install -r requirements.txt
RUN test -f /root/.ssh/id_rsa || ssh-keygen -f /root/.ssh/id_rsa -t rsa -P ''
RUN echo -e "Host *\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile /dev/null" > /root/.ssh/config

COPY . /opt/fit2ansible
VOLUME /opt/fit2ansible/data
RUN echo > config.yml

ENV LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8
ENV PYTHONOPTIMIZE=1
ENV C_FORCE_ROOT=1

EXPOSE 8080
EXPOSE 8081
ENTRYPOINT ["./entrypoint.sh"]
