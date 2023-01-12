FROM python:3

RUN mkdir -p /opt/src/applications
WORKDIR /opt/src/applications

COPY applications/admin/application.py ./admin/application.py
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/roleCheck.py ./roleCheck.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/"
ENTRYPOINT ["python", "./admin/application.py"]