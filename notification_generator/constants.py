from enum import Enum


class NotificationStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class TaskType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
