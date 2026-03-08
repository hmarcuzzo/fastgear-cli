import questionary

from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.exceptions import InvalidInputError

MODULE_PROMPT_CHOICES: tuple[ElementTypeEnum, ...] = (
    ElementTypeEnum.CONTROLLER,
    ElementTypeEnum.SERVICE,
    ElementTypeEnum.REPOSITORY,
    ElementTypeEnum.ENTITY,
)
MODULE_GENERATION_ORDER: tuple[ElementTypeEnum, ...] = (
    ElementTypeEnum.ENTITY,
    ElementTypeEnum.REPOSITORY,
    ElementTypeEnum.SERVICE,
    ElementTypeEnum.CONTROLLER,
)


def resolve_module_components(module_components: str | None) -> list[ElementTypeEnum]:
    if module_components is None:
        selected = questionary.checkbox(
            "Which components do you want to add to this module?",
            choices=[choice.value for choice in MODULE_PROMPT_CHOICES],
        ).ask()
        values = selected or []
    else:
        values = [item.strip().lower() for item in module_components.split(",") if item.strip()]

    return parse_module_components(values)


def parse_module_components(values: list[str]) -> list[ElementTypeEnum]:
    if not values:
        raise InvalidInputError(
            "At least one component is required for module. Use: controller, service, repository, entity."
        )

    selected: set[ElementTypeEnum] = set()
    valid_components = {choice.value for choice in MODULE_PROMPT_CHOICES}

    for value in values:
        if value not in valid_components:
            raise InvalidInputError(
                "Invalid module component. Use only: controller, service, repository, entity."
            )
        selected.add(ElementTypeEnum(value))

    return [component for component in MODULE_GENERATION_ORDER if component in selected]
