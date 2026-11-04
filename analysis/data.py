import numpy as np
import pandas as pd

CUTOFF = pd.Timestamp("2026-09-30")


def generate(seed=42, n=18000):
    rng = np.random.default_rng(seed)
    users, events = [], []
    for uid in range(n):
        installed = pd.Timestamp("2026-08-01") + pd.Timedelta(days=int(rng.integers(0, 61)))
        channel = rng.choice(["organic", "paid", "referral"])
        engaged = rng.beta(2, 3)
        onboarded = rng.random() < 0.25 + 0.6 * engaged
        users.append((uid, installed, channel, onboarded))
        for day in range(31):
            at = installed + pd.Timedelta(days=day)
            probability = (0.07 + 0.65 * engaged) * np.exp(-day / 35)
            if at <= CUTOFF and (day == 0 or rng.random() < probability):
                events.append((uid, at))
    users = pd.DataFrame(users, columns=["user_id", "installed_at", "channel", "onboarded"])
    events = pd.DataFrame(events, columns=["user_id", "active_at"])
    return users, pd.concat(
        [events, events.sample(frac=0.02, random_state=seed)], ignore_index=True
    )
