from sheet import PermissionState, SheetsDatabase
from sugar import ArgumentShell
from safe_eval import arithmetics_eval

app = ArgumentShell()
db = SheetsDatabase()


@app.command()
def user(username: str) -> None:
    """Create a new user"""
    db.post_user(username)


@app.command()
def sheet(username: str, sheetid: str) -> None:
    """Create a new sheet"""
    user = db.get_user(username)
    db.post_sheet(user, sheetid)


@app.command()
def check(username: str, sheetid: str) -> None:
    """Check a sheet"""
    user = db.get_user(username)
    sheet = db.get_sheet(user, sheetid)
    if sheet is not None:
        print(sheet)


@app.command()
def patch(username: str, sheetid: str, row: int, col: int, expr: str) -> None:
    """Patch a sheet"""
    value = arithmetics_eval(expr)
    if value is None:
        return
    user = db.get_user(username)
    db.patch_sheet(user, sheetid, row, col, value)


@app.command()
def chmod(username: str, sheetid: str, state: PermissionState) -> None:
    """Change permissions"""
    user = db.get_user(username)
    db.chmod(user, user, sheetid, state)


@app.command()
def share(username: str, sheetid: str, other: str) -> None:
    """Share a sheet to another user"""
    user1 = db.get_user(username)
    user2 = db.get_user(other)
    db.chmod(user1, user2, sheetid, PermissionState.EDITABLE)


if __name__ == "__main__":
    app.run()
