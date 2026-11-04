import pandas as pd
import pytest

from analysis.__main__ import retention


def test_censoring_duplicates_and_exact_day():
    users = pd.DataFrame(
        {
            "user_id": [1, 2, 3],
            "installed_at": pd.to_datetime(["2026-08-01", "2026-08-01", "2026-09-20"]),
            "channel": ["organic"] * 3,
            "onboarded": [True] * 3,
        }
    )
    events = pd.DataFrame(
        {
            "user_id": [1, 1, 2, 3],
            "active_at": pd.to_datetime(["2026-08-31", "2026-08-31", "2026-09-01", "2026-09-21"]),
        }
    )
    result = retention(users, events, pd.Timestamp("2026-09-30"))
    d30 = result.query("day == 30")
    assert d30.eligible_users.sum() == 2
    assert d30.retained_users.sum() == 1
    assert d30.retention.iloc[0] == 0.5
    assert result.query("day == 1").eligible_users.sum() == 3


def test_duplicate_installation_rejected():
    users = pd.DataFrame({"user_id": [1, 1]})
    with pytest.raises(ValueError, match="Duplicate"):
        retention(users, pd.DataFrame(), pd.Timestamp("2026-09-30"))
