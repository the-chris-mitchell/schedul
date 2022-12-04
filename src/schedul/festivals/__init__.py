import os
from models.festival import Festival


try:
    for module in os.listdir(f"{os.path.dirname(__file__)}/custom"):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        module_name = f"festivals.custom.{module[:-3]}"
        __import__(module_name, locals(), globals())
except (ModuleNotFoundError, FileNotFoundError) as err:
    raise Exception("Festival missing, please add one under ./festivals/custom").with_traceback(err.__traceback__) from err


def get_festivals() -> list[Festival]:
    return [cls() for cls in Festival.__subclasses__()]  # type: ignore

FESTIVALS = get_festivals()