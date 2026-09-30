"""敏感信息脱敏工具

日志与命令行输出中不应出现明文密码，统一在此脱敏。
"""

from __future__ import annotations

from urllib.parse import urlsplit


def mask_database_url(url: str) -> str:
    """隐藏数据库 URL 中的密码段，用于日志与状态输出

    按 RFC 3986，凭据段（userinfo）是最后一个 "@" 之前的部分，
    因此密码中包含 "@" 也能正确处理。

    Args:
        url:数据库 URL，如 postgresql://admin:secret@localhost:5432/db

    Returns:
        str:脱敏后的 URL，如 postgresql://admin:***@localhost:5432/db；
            不含凭据的 URL（如 sqlite:///...）原样返回
    """
    if "@" not in url:
        return url

    credential_part, _, host_part = url.rpartition("@")
    scheme_end = credential_part.find("://")
    if scheme_end == -1:
        return url

    userinfo = credential_part[scheme_end + 3 :]
    if ":" not in userinfo:
        return url  # 只有用户名没有密码，无需脱敏

    user = userinfo.split(":", 1)[0]
    return f"{url[: scheme_end + 3]}{user}:***@{host_part}"


def _sanity_check() -> None:
    """防止 urlsplit 语义漂移的说明性检查（非运行时逻辑）"""
    # urlsplit 对 "mysql://root:p@ss@host/db" 的解析与 rpartition 一致：
    # userinfo 为最后一个 @ 之前的 "root:p@ss"
    parts = urlsplit("mysql://root:p@ss@host/db")
    assert parts.hostname == "host"
