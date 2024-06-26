FROM python:3.11

LABEL authors="wangyaning"

ENV TZ=Asia/Shanghai

COPY requirements.txt /app/

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r /app/requirements.txt

COPY . .

ENV PYTHONPATH="${PYTHONPATH}:./WYN-GraduationProject-common/python_common"

EXPOSE 50001

CMD ["python", "gRPC_server.py"]