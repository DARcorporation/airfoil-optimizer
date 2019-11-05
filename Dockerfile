FROM danieldv/hode:latest

# ======================= SSH Setup ======================
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN service ssh restart

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
# ======================= SSH Setup ======================

# ===================== Af Opt Setup =====================
USER root
WORKDIR /tmp

# Prerequisites
RUN apt-get -qq update && \
    apt-get install -y --no-install-recommends apt-utils && \
    apt-get -y install nano && \
    apt-get -y purge cmake && \
    apt-get -y autoremove && \
    pip3 install 'cmake>=3.12'

# Install requirements with pip
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade -r requirements.txt

# Install XFOIL
RUN wget -O xfoil.tar.gz https://github.com/daniel-de-vries/xfoil-python/archive/1.1.0.tar.gz && \
    tar -xzf xfoil.tar.gz && \
    pip3 install ./xfoil-python-1.1.0 && \
    rm -rf /tmp/* && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install af_opt
COPY ./af_opt /tmp/af_opt
COPY ./setup.py /tmp/
RUN python3 /tmp/setup.py install
# ===================== Af Opt Setup =====================

EXPOSE 22
CMD /usr/sbin/sshd -D
