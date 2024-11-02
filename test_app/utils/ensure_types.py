import typing


def ensure_str(v: typing.Union[str, bytes], *, encoding: str = "utf-8") -> str:
    """Make sure we have a str."""
    return v.decode(encoding) if isinstance(v, bytes) else v


def ensure_bytes(v: typing.Union[str, bytes], *, encoding: str = "utf-8") -> bytes:
    """Make sure we have a bytes."""
    return v.encode(encoding) if isinstance(v, str) else v
