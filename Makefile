# 定义变量
PROTO_DIR = ../WYN-GraduationProject-proto
OUT_DIR = ./pyproto
PROTO_FILE = response.proto

# 默认目标
all: generate

# 生成Python gRPC代码的规则
generate:
	python3 -m grpc_tools.protoc --python_out=$(OUT_DIR) --grpc_python_out=$(OUT_DIR) -I$(PROTO_DIR) $(PROTO_DIR)/$(PROTO_FILE)

# 清理生成的文件
clean:
	rm -f $(OUT_DIR)/*_pb2.py $(OUT_DIR)/*_pb2_grpc.py

.PHONY: all generate clean
