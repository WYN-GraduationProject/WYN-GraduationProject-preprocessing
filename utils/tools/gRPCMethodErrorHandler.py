from functools import wraps
from typing import Iterable, TypeVar, Tuple, Type, Optional

from grpc import StatusCode
from grpc.aio import ServicerContext, AioRpcError

__all__ = ['grpc_method_error_handler']

SomeException = TypeVar('SomeException', bound=Exception)


def grpc_method_error_handler(exceptions: Optional[Iterable[Tuple[Type[SomeException], str, bool]]] = None):
    """
    gRPC服务方法，注册出错并在出错时自动调用context.abort
    :param exceptions: 包含可能出现的异常及其响应信息的可迭代的多个元组
    """

    def decorator(func):
        @wraps(func)
        async def wrapped_function(self, request, context: ServicerContext):
            try:
                return await func(self, request, context)
            except Exception as e:
                if isinstance(e, AioRpcError):
                    await context.abort(code=e.code(), details=e.details())
                if exceptions is None:
                    raise e
                for error, error_info, is_excepted_error in exceptions:
                    if isinstance(e, error):
                        await context.abort(
                            code=(StatusCode.INVALID_ARGUMENT if is_excepted_error else StatusCode.UNAVAILABLE),
                            details=error_info
                        )
                raise e

        return wrapped_function

    return decorator
