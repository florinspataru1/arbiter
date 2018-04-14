FROM node:alpine

RUN apk add --no-cache python python-dev python3 python3-dev \
    linux-headers build-base bash git ca-certificates && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    rm -r /root/.cache

RUN cd ~ && git clone https://github.com/florinspataru1/arbiter.git arbiter
RUN cd ~/arbiter && chmod a+x *.sh && mkdir -p log && mkdir -p mocks

WORKDIR /root/arbiter
# Container entry point
ENTRYPOINT ["/root/arbiter/entrypoint.sh"]
CMD ["start"]