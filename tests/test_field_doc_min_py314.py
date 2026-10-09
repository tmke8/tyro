"""Test helptext from `dataclasses.field(doc=...)`, which was added in Python 3.14.

This test file requires Python 3.14+.
"""

import dataclasses
from typing import Any

from helptext_utils import get_helptext_with_checks
from typing_extensions import Annotated, Doc

import tyro


def field_with_doc(doc: str, **kwargs: Any) -> Any:
    """Thin wrapper around `dataclasses.field(doc=...)`. The type checkers in
    CI are configured for Python <3.14, where the `doc` argument doesn't exist
    yet."""
    return dataclasses.field(doc=doc, **kwargs)  # type: ignore


def test_field_doc_basic() -> None:
    @dataclasses.dataclass
    class Config:
        x: int = field_with_doc("Documentation for x.")
        y: str = field_with_doc("Documentation for y.", default="hi")

    helptext = get_helptext_with_checks(Config)
    assert "Documentation for x." in helptext
    assert "Documentation for y." in helptext


def test_field_doc_with_default_factory() -> None:
    @dataclasses.dataclass
    class Config:
        x: list[int] = field_with_doc("Documentation for x.", default_factory=list)

    assert "Documentation for x." in get_helptext_with_checks(Config)


def test_field_doc_multiline_dedent() -> None:
    @dataclasses.dataclass
    class Config:
        x: int = field_with_doc(
            """
            This is a multiline
            documentation string
            that should be dedented.
            """
        )

    helptext = get_helptext_with_checks(Config)
    assert "multiline documentation" in helptext
    assert "string that" in helptext


@dataclasses.dataclass
class Inner:
    """Inner docstring."""

    a: int = field_with_doc("Documentation for a.", default=1)


@dataclasses.dataclass
class Outer:
    inner: Inner = field_with_doc("Documentation for inner.", default_factory=Inner)


def test_field_doc_nested() -> None:
    helptext = get_helptext_with_checks(Outer)
    assert "Documentation for a." in helptext
    assert "Documentation for inner." in helptext
    assert "Inner docstring." not in helptext


def test_field_doc_overrides_docstring_and_comment() -> None:
    @dataclasses.dataclass
    class Config:
        # Comment for x.
        x: int = field_with_doc("Field doc for x.")
        y: int = field_with_doc("Field doc for y.")
        """Attribute docstring for y."""

    helptext = get_helptext_with_checks(Config)
    assert "Field doc for x." in helptext
    assert "Comment for x." not in helptext
    assert "Field doc for y." in helptext
    assert "Attribute docstring for y." not in helptext


def test_pep727_doc_overrides_field_doc() -> None:
    @dataclasses.dataclass
    class Config:
        x: Annotated[int, Doc("PEP 727 doc for x.")] = field_with_doc(
            "Field doc for x."
        )

    helptext = get_helptext_with_checks(Config)
    assert "PEP 727 doc for x." in helptext
    assert "Field doc for x." not in helptext


def test_arg_help_overrides_field_doc() -> None:
    @dataclasses.dataclass
    class Config:
        x: Annotated[int, tyro.conf.arg(help="Arg help for x.")] = field_with_doc(
            "Field doc for x."
        )
        y: Annotated[
            int, tyro.conf.arg(help="Arg help for y."), Doc("PEP 727 doc for y.")
        ] = field_with_doc("Field doc for y.")

    helptext = get_helptext_with_checks(Config)
    assert "Arg help for x." in helptext
    assert "Field doc for x." not in helptext
    assert "Arg help for y." in helptext
    assert "PEP 727 doc for y." not in helptext
    assert "Field doc for y." not in helptext


def test_field_doc_falls_back_to_docstring_when_unset() -> None:
    @dataclasses.dataclass
    class Config:
        x: int = dataclasses.field(default=3)
        """Attribute docstring for x."""
        y: int = field_with_doc("Field doc for y.", default=4)

    helptext = get_helptext_with_checks(Config)
    assert "Attribute docstring for x." in helptext
    assert "Field doc for y." in helptext
