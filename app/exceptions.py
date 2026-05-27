class BusinessException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFound(BusinessException):
    def __init__(self, resource: str, resource_id):
        super().__init__("NOT_FOUND", f"{resource} {resource_id} 不存在", 404)


class PermissionDenied(BusinessException):
    def __init__(self, message: str = "无权访问此资源"):
        super().__init__("PERMISSION_DENIED", message, 403)
