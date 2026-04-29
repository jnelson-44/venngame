import re
import typer
from rich import print
from src.lib.Puzzle import Criteria


app = typer.Typer(no_args_is_help=True)

def _get_subclasses(clazz):
    subs = []
    for subclass in clazz.__subclasses__():
        subs.append(subclass)
        subs.extend(_get_subclasses(subclass))
    return subs

###########################################
## SCRIPT COMMAND: LIST AVAILABLE        ##
###########################################
@app.command("list")
def list_criteria():
    for crit in _get_subclasses(Criteria.Criterion):
        match = re.search(r"Criteria.(?P<class_name>.+\.[a-zA-Z]+)'>$", str(crit))
        if not match:
            continue
        print(match.group("class_name"))

@app.command()
def test():
    pass

###########################################
## SCRIPT ROOT INVOCATION                ##
###########################################

if __name__ == "__main__":
    app()
