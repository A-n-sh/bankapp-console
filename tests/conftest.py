from datetime import datetime, timedelta, timezone

import pytest

from bankapp.service import BankService
from bankapp.storage import Repository


class Clock:
    def __init__(self):
        self.now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.now

    def advance(self, **kwargs):
        self.now += timedelta(**kwargs)


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def repo():
    r = Repository(":memory:")
    yield r
    r.close()


@pytest.fixture
def service(repo, clock):
    return BankService(repo, now=clock)
