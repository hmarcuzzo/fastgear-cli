from enum import StrEnum


class ElementTypeEnum(StrEnum):
    MODULE = "module"
    CONTROLLER = "controller"
    SERVICE = "service"
    ENTITY = "entity"
    REPOSITORY = "repository"
