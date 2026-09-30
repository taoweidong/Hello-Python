"""安全工具测试"""

import pytest

from src.core.utils import mask_database_url


class TestMaskDatabaseUrl:
    """数据库 URL 脱敏测试"""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("postgresql://admin:secret@localhost:5432/db", "postgresql://admin:***@localhost:5432/db"),
            ("mysql://root:p@ss@127.0.0.1:3306/app", "mysql://root:***@127.0.0.1:3306/app"),
            ("sqlite:///./data/app.db", "sqlite:///./data/app.db"),
            ("sqlite:///:memory:", "sqlite:///:memory:"),
            ("", ""),
        ],
    )
    def test_mask(self, raw: str, expected: str) -> None:
        assert mask_database_url(raw) == expected

    def test_original_url_not_mutated(self) -> None:
        raw = "postgresql://admin:secret@localhost/db"
        mask_database_url(raw)
        assert "secret" in raw
