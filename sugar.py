"""
Simple
Utility for
Generating
Argparse-based
Runner
"""

import sys
from argparse import ArgumentError, ArgumentParser
from ast import literal_eval
from collections.abc import Callable
from functools import cache, partial, wraps
from inspect import getdoc, signature
from shlex import split
from typing import Any, NoReturn, Sequence

__all__ = ["ArgumentShell"]


@cache
def _literal_eval_type[T](type_: Callable[[Any], T]) -> Callable[[str], T]:
    @wraps(type_)
    def handler(x: str) -> T:
        try:
            lit = literal_eval(x)
        except SyntaxError:
            raise ValueError(f"invalid syntax: {x}")
        else:
            return type_(lit)

    return handler


def _add_arguments(parser: ArgumentParser, obj: Callable[..., Any]) -> None:
    parser.description = getdoc(obj)
    sig = signature(obj, eval_str=True)

    for arg, param in sig.parameters.items():
        kwargs = {}

        annotation = param.annotation

        if annotation is not param.empty:
            if not issubclass(annotation, str):
                annotation = _literal_eval_type(annotation)

            kwargs["type"] = annotation

        if param.kind == param.POSITIONAL_ONLY:
            args = (arg,)
        elif param.kind == param.POSITIONAL_OR_KEYWORD:
            args = (arg,)
        elif param.kind == param.KEYWORD_ONLY:
            args = (f"-{arg[0]}", f"--{arg}")
        else:
            raise ValueError(f"unsupported parameter kind: {param.kind}")

        parser.add_argument(*args, **kwargs)


class _ArgumentParser(ArgumentParser):
    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        try:
            super().exit()
        except SystemExit:
            raise ArgumentError(None, message or "")


class ArgumentShell:
    def __init__(self) -> None:
        self.commands = {}
        self.parser = _ArgumentParser(prog="", add_help=False, exit_on_error=False)
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        self.add_command(lambda: self.parser.print_help(), name="help")

    def command[T: Callable[..., Any]](self, name: str = "") -> Callable[[T], T]:
        return partial(self.add_command, name=name)

    def add_command[T: Callable[..., Any]](self, obj: T, *, name: str = "") -> T:
        key = name or getattr(obj, "__name__", None)

        if key is None:
            raise ValueError("name is required if not using a function")

        if not key:
            raise ValueError("name must not be empty")

        if key in self.commands:
            raise ValueError(f"duplicate command: {key}")

        self.commands[key] = obj
        subparser = self.subparsers.add_parser(key, exit_on_error=False)
        _add_arguments(subparser, obj)

        return obj

    def parse_agrs(self, args: Sequence[str] | None = None) -> None:
        try:
            ns = self.parser.parse_args(args)
        except ArgumentError as e:
            if e.message:
                print(e.message, file=sys.stderr)
            return
        v = vars(ns)
        key = v.pop("command", "help")
        subcommand = self.commands[key]
        subcommand(**v)

    def parse_str(self, x: str) -> None:
        try:
            args = split(x)
        except ValueError as e:
            print(e, file=sys.stderr)
        else:
            self.parse_agrs(args)

    def run(
        self,
        *,
        prompt: str = "> ",
    ) -> None:
        while True:
            try:
                x = input(prompt)
            except EOFError:
                break
            else:
                self.parse_str(x)
