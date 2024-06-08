from sheet import SheetsDatabase
from sugar import ArgumentShell

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
def patch(username: str, sheetid: str, row: int, col: int, value: int) -> None:
    """Patch a sheet"""
    user = db.get_user(username)
    db.patch_sheet(user, sheetid, row, col, value)


if __name__ == "__main__":
    app.run()
