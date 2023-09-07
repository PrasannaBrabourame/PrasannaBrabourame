from dataclasses import dataclass
from typing import Tuple


class Meta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        return dataclass(unsafe_hash=True, frozen=True)(new_cls)


class Bio(metaclass=Meta):
    name        : str = "Prasanna Brabourame"
    designation : str = "Solution Architect / Tech Lead"
    company     : str = "NCS Pte Ltd"
    base        : str = "Singapore"
    blog        : str = "https://prasannabrabourame.medium.com/"


class Stack(metaclass=Meta):
    languages   : Tuple[str, ...] = ("GO", "NodeJS", "Python", "C#")
    databases   : Tuple[str, ...] = ("MySQL", "PostgreSQL", "Mongo", "Redis", "DynamoDB", "Elastic Search", "MSSQL")
    misc        : Tuple[str, ...] = ("Docker", "Celery", "ML", "DL")
    Cloud       : Tuple[str, ...] = ("AWS", "Azure", "GCP")
    ongoing     : Tuple[str, ...] = ("Dapr", "Terraform")


class Social(metaclass=Meta):
    twitter     : str = "prasannabrabour"
    linkedin    : str = "prasannabrabourame"