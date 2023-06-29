from pathlib import Path


def get_project_root(return_type="str"):
    """
    Gets the path to the project root.

    Parameters
    ----------
    return_type: str
        Determine whether simple str or path object should be returned (options: "str" or "path").

    Returns
    -------
    str | Path
        Path or string to the project root.

    """
    if return_type == "str":
        output = str(Path(__file__).parent.parent.parent.parent)
    elif return_type == "path" or return_type == "Path":
        output = Path(__file__).parent.parent.parent.parent
    else:
        raise ValueError("Wrong return type supplied.")

    return output
