FROM python:3.10 as py310-base
RUN apt -y update &&\
    apt-get install -y git &&\
    apt -y install build-essential &&\
    apt-get clean &&\
    pip install -U pip
WORKDIR /home/app

FROM py310-base as builder
COPY . .
RUN pip install .[dev,deploy]
RUN nox -s run_tests
RUN python -m build

FROM py310-base
COPY --from=builder /home/app/dist/*.whl .
RUN pip install *.whl &&\
    rm *.whl
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["echo", "Hello, World!"]
