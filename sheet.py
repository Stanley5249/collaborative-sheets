from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial
from typing import Protocol

__all__ = ["SheetsDatabase", "User", "Sheet"]

# ================================================================
# datamodels
# ================================================================


def make_matrix(row: int, col: int) -> list[list[float]]:
    return [[0.0] * col for _ in range(row)]


@dataclass
class User:
    name: str


@dataclass
class Sheet:
    id: str
    data: list[list[float]] = field(default_factory=partial(make_matrix, 3, 3))

    def __str__(self) -> str:
        return "\n".join(" ".join(format(x, "5.3g") for x in row) for row in self.data)


# ================================================================
# sheet permission proxies
# ================================================================


class SheetPermission(Protocol):
    def post(self, sheets: dict[str, Sheet], sheetid: str) -> Sheet | None:
        if sheetid in sheets:
            print(f"sheet {sheetid} already exists")
            return

        sheets[sheetid] = sheet = Sheet(sheetid)
        print(f"sheet {sheetid} created")
        return sheet

    def get(self, sheets: dict[str, Sheet], sheetid: str) -> Sheet | None:
        if sheetid not in sheets:
            print(f"sheet {sheetid} does not exist")
            return

        print(f"sheet {sheetid} retrieved")
        return sheets[sheetid]

    @abstractmethod
    def patch(
        self, sheets: dict[str, Sheet], sheetid: str, row: int, col: int, val: float
    ) -> Sheet | None: ...


class SheetReadOnly(SheetPermission):
    def patch(
        self, sheets: dict[str, Sheet], sheetid: str, row: int, col: int, val: float
    ) -> Sheet | None:
        print(f"sheet {sheetid} is read-only")


class SheetEditable(SheetPermission):
    def patch(
        self, sheets: dict[str, Sheet], sheetid: str, row: int, col: int, val: float
    ) -> Sheet | None:
        sheet = self.get(sheets, sheetid)
        if sheet is None:
            return

        sheet.data[row][col] = val
        print(f"sheet {sheetid} updated")
        return sheet


# ================================================================
# database
# ================================================================


@dataclass
class SheetsDatabase:
    users: dict[str, User] = field(default_factory=dict)
    sheets: dict[str, Sheet] = field(default_factory=dict)
    manager: dict[tuple[str, str], SheetPermission] = field(
        default_factory=partial(defaultdict, SheetReadOnly)
    )

    # ================================================================
    # user operations
    # ================================================================

    def get_user(self, username: str) -> User | None:
        if username not in self.users:
            print(f"user {username} does not exist")
            return

        print(f"user {username} retrieved")
        return self.users[username]

    def post_user(self, username: str) -> User | None:
        if username in self.users:
            print(f"user {username} already exists")
            return

        self.users[username] = user = User(username)
        print(f"user {username} created")
        return user

    # ================================================================
    # sheet operations with permission
    # ================================================================

    def get_sheet(self, user: User | None, sheetid: str) -> Sheet | None:
        if user is None:
            return
        permmision = self.manager[user.name, sheetid]
        return permmision.get(self.sheets, sheetid)

    def post_sheet(self, user: User | None, sheetid: str) -> Sheet | None:
        if user is None:
            return
        permmision = self.manager[user.name, sheetid]
        return permmision.post(self.sheets, sheetid)

    def patch_sheet(
        self, user: User | None, sheetid: str, row: int, col: int, val: float
    ) -> Sheet | None:
        if user is None:
            return
        permmision = self.manager[user.name, sheetid]
        return permmision.patch(self.sheets, sheetid, row, col, val)
