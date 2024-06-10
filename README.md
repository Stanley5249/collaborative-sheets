# Collaborative Sheets

This project is a demonstration and conceptual template from a Programming Language Design course, intended for educational purposes only. It is not designed to be a real product or tool.

## Features

- **User Management**: Create and manage users.
- **Sheet Management**: Users can create new sheets, print out their sheets, and change the content of their sheets.
- **Access Control**: Sheets have two access rights (read-only or editable). Users can share their sheets with other users.
- **Arithmetic Operations**: Sheets support rational arithmetic (`+`, `-`, `*`, `/`). Handles rational numbers like `123.456`, `123` and operators like `+`, `-`, `*`, `/`.
- **Modular Access Control**: Easily switch on/off access rights and sharing functionality by modifying specific parts of the code.

## Environment

- **Python Version**: 3.12

## How to Use

To run the application, execute the following command in the command line:

```
python main.py
```

This will start the application and allow you to interact with it using the provided commands:

- **help**
    - Outputs the list of available commands.

- **user `<user_name>`**
    - Creates a user with the specified `<user_name>`.

- **sheet `<user_name>` `<sheet_name>`**
    - Creates a sheet named `<sheet_name>` for the user `<user_name>`.

- **check `<user_name>` `<sheet_name>`**
    - Displays the content of the sheet named `<sheet_name>` for the user `<user_name>`.

- **patch `<user_name>` `<sheet_name>` `<row_number>` `<col_number>` `<number>`**
    - Modifies the content at position (`<row_number>`, `<col_number>`) of the sheet `<sheet_name>` for the user `<user_name>` to `<number>`.

- **chmod `<user_name>` `<sheet_name>` `<readonly/editable>`**
    - Changes the access rights of the sheet `<sheet_name>` for the user `<user_name>` to either read-only or editable.

- **share `<user_name_a>` `<sheet_name>` `<user_name_b>`**
    - Shares the sheet `<sheet_name>` from user `<user_name_a>` to user `<user_name_b>`.

## Implementation Details

### main.py

Main program which decorates commands in `ArgumentShell` to define the behavior of each command.

### safe_eval.py

Safe arithmetic evaluation:
- Parses and evaluates arithmetic expressions securely.
- Supports operations: `+`, `-`, `*`, `/`, `%`, `**`, `//`, scientific notation, and other number bases.

### sheet.py

Defines data types and operations:

- **User**
  - **Attributes**: `name` (string)

- **Sheet**
  - **Attributes**: `id` (string), `data` (list[list[float]])
  - **Behavior**: `patch(row, column, value)` modifies the data.

- **Permission (Enum)**
  - Values: `READONLY`, `EDITABLE`

- **SheetPermission**
  - **Attributes**: `is_owner` (bool)
  - **Behavior**: 
    - `post(sheets, manager, username, sheetid)`
    - `get(sheets, sheetid)`
    - `patch(sheets, sheetid, row, column, value)`
    - `chmod(manager, username, sheetid, state)`

- **SheetReadOnly (extends SheetPermission)**
  - **Behavior**: `patch(sheets, sheetid, row, column, value)`

- **SheetEditable (extends SheetPermission)**
  - **Behavior**: `patch(sheets, sheetid, row, column, value)`

- **SheetDatabase**
  - **Attributes**: `users` (dict), `sheets` (dict), `manager` (dict)
  - **Behavior**: 
    - `get_user(username)`
    - `post_user(username)`
    - `get_sheet(user, sheetid)`
    - `post_sheet(user, sheetid)`
    - `patch_sheet(user, sheetid, row, column, value)`
    - `chmod(user1, user2, sheetid, state)`

### sugar.py

Command management:
- Adds commands to `ArgumentShell` and parser.
- Parses and executes the corresponding functions for each command.

## Disabling chmod and share Functions

To disable `chmod` and `share` functionality:
- Remove or comment out the corresponding functions in `main.py`.
- Verify by running `help` or the specific command.

## Program Paradigm

### Used

#### Object-Oriented Programming (OOP)

- **Features**: Encapsulation, Inheritance, Polymorphism, Reduced maintenance and extension efforts.
- **Application**: 
  - Classes are encapsulated, accessed only through provided interfaces.
  - `readonly` and `editable` inherit from `Permission` and override `patch` for polymorphism in `SheetDatabase`.
  - Use of `typing.Protocol` in `SheetPermission` class to define a common interface without requiring inheritance. This allows for more flexible and decoupled code design, as different classes can implement the protocol without being tightly bound to a specific class hierarchy.

#### Metaprogramming

- **Features**: Code that writes or manipulates other code, typically at compile time or runtime.
- **Application in `sugar.py`**: 
  - Utilizes decorators like `@app.command` to dynamically add commands to the `ArgumentShell`.
  - Inspects type annotations at runtime to ensure proper command parsing and execution.
  - Example from `sugar.py` and `main.py`:
    - `@app.command` decorator inspects function signatures and type annotations to register commands dynamically.
    - This allows for flexible command definitions and ensures that type constraints are enforced when commands are executed.

### Not Used

#### Event-Driven Programming

- **Features**: Control flow by user actions or messages, Dynamic callback setting, Asynchronous execution, Low coupling.
- **Potential Application**: 
  - Use buttons instead of command input.
  - Objects publish events to observers (Observer Pattern).

## Design Patterns

### Used

#### Strategy Pattern

- **Features**: Encapsulates different behaviors, easy to switch and extend, avoids excessive if-else.
- **Application**:
  - Define `Permission` base class with `readonly` and `editable` inheriting.
  - Different `patch` behaviors implemented in `readonly` and `editable`.
  - `manager` executes stored permissions (polymorphism).
  - Switch behaviors by assigning corresponding permissions to `manager`.

### Not Used

#### Observer Pattern

- **Features**: Observers notified of changes in the observable object.
- **Potential Application**: 
  - Users with access have their own sheet copy.
  - `user` implements `observer`, `sheet` implements `observable`.
  - Users register as observers to the sheet.
  - Changes notify all observers to update.

---

## Errors Encountered During Programming

No real bugs were encountered that required a debugger, but there are still some important points to share.

### Permission

Implementing detailed permission assessment raised some questions. Specifically, if an owner changes their permission to read-only, should they be able to change it back to editable? If allowed, since the default permission is read-only, anyone could modify the permission to editable, compromising security. If not allowed, the owner can never regain access permissions, rendering the sheet unmodifiable.

We temporarily solved this by adding an owner flag to the permission object, which restricts the `chmod` behavior to be callable only by the owner.

### Expression Evaluation

Safely evaluating an expression via Python's built-in `eval` is not possible, so a custom implementation is necessary. Parsing a binary operation is straightforward but traditionally not extensible.

We used the built-in `ast` module and the `match` statement to validate that the syntax is either a numeric binary operation or a numeric constant. This approach is interesting and worth checking out.

### Shell

Python's built-in `cmd` module supports shell-like programs but can access the real shell, which can be dangerous. Other third-party shell libraries exist but hardly fit this scenario, so we rebuilt the shell from scratch.

Introducing `SUGAR` (Simple Utility for Generating Argparse-based Runner). As its name suggests, it uses another built-in library, `argparse`, a CLI library, as the parser for each command.

Furthermore, it inspects annotations at runtime, as described in the metaprogramming section. Thus, we can easily add and remove commands by simply commenting out one line of code, without needing to modify the parser when parameters change. This approach is inspired by `Fire` and `Typer`, two well-known Python third-party CLI libraries.

How did I come up with this? I frequently encounter the need for a shell-like library in everyday coding, but third-party libraries sometimes do not match my requirements. Submitting a feature request can be time-consuming, so I created `SUGAR`. It is intended to be published to PyPI once the basic features are completed.