# 定义变量
PROTO_DIR := ../WYN-GraduationProject-common/proto
OUT_DIR := ./pyproto

# 检测操作系统
ifeq ($(OS),Windows_NT)
    detected_OS := Windows
	PROTO_DIR := H:\WYN-GraduationProject\Source\backend\WYN-GraduationProject-common\proto
    # Windows下查找所有.proto文件的命令
    PROTO_FILES := $(shell dir /s /b $(PROTO_DIR)\\*.proto)
    RM := del /Q /F
else
    detected_OS := $(shell uname -s)
    # Unix-like系统下查找所有.proto文件的命令
    PROTO_FILES := $(shell find $(PROTO_DIR) -name '*.proto')
    RM := rm -f
endif

# 打印所有.proto文件
$(info $(PROTO_FILES))
$(info $(PROTO_DIR))

# 默认目标
all: generate

# 生成Python gRPC代码的规则
generate:
ifeq ($(detected_OS),Windows)
	@for /r $(PROTO_DIR) %%f in (*.proto) do ( \
		python -m grpc_tools.protoc --python_out=$(OUT_DIR) --grpc_python_out=$(OUT_DIR) -I$(PROTO_DIR) %%f \
	)
else
	@for proto in $(PROTO_FILES); do \
		python3 -m grpc_tools.protoc --python_out=$(OUT_DIR) --grpc_python_out=$(OUT_DIR) -I$(PROTO_DIR) $$proto; \
	done
endif

# 清理生成的文件
clean:
	$(RM) $(OUT_DIR)/*_pb2.py $(OUT_DIR)/*_pb2_grpc.py

.PHONY: all generate clean
