import math

import duckdb
import matplotlib.pyplot as plt

from .common import DATA, REPORTS, ROOT, prepare, save_metrics
from .data import CUTOFF, generate


def retention(users, events, cutoff):
    if users.user_id.duplicated().any():
        raise ValueError("Duplicate installations")
    if not events.user_id.isin(users.user_id).all():
        raise ValueError("Activity without installation")
    with duckdb.connect() as con:
        con.register("users", users)
        con.register("events", events)
        return con.execute((ROOT / "sql/retention.sql").read_text(), {"cutoff": cutoff}).df()


def main():
    prepare()
    users, events = generate()
    users.to_csv(DATA / "users.csv", index=False)
    events.to_csv(DATA / "events.csv", index=False)
    result = retention(users, events, CUTOFF)
    result.to_csv(REPORTS / "cohorts.csv", index=False)
    grouped = result.groupby(["day", "onboarded"])[["eligible_users", "retained_users"]].sum()
    grouped["retention"] = grouped.retained_users / grouped.eligible_users
    grouped.to_csv(REPORTS / "onboarding.csv")
    d30 = grouped.loc[30]
    ratio = float(d30.loc[True, "retention"] / d30.loc[False, "retention"])
    totals = result.groupby(["cohort", "day"])[["eligible_users", "retained_users"]].sum()
    heatmap = (totals.retained_users / totals.eligible_users).unstack("day")
    fig, ax = plt.subplots(figsize=(7.5, 5))
    im = ax.imshow(heatmap, cmap="Blues", vmin=0, vmax=0.5, aspect="auto")
    ax.set(
        xticks=range(3),
        xticklabels=["D1", "D7", "D30"],
        yticks=range(len(heatmap)),
        yticklabels=[str(d.date()) for d in heatmap.index],
        title="Exact-day retention by install week",
    )
    for row in range(len(heatmap)):
        for col in range(3):
            value = heatmap.iloc[row, col]
            ax.text(
                col, row, "—" if math.isnan(value) else f"{value:.1%}", ha="center", va="center"
            )
    fig.colorbar(im, ax=ax, label="Retention")
    fig.tight_layout()
    fig.savefig(REPORTS / "retention.png", dpi=160)
    metrics = {
        "users": len(users),
        "cutoff": str(CUTOFF.date()),
        "d30_onboarding_ratio": ratio,
        "d30_onboarded": float(d30.loc[True, "retention"]),
        "d30_not_onboarded": float(d30.loc[False, "retention"]),
        "d30_eligible": int(d30.eligible_users.sum()),
    }
    save_metrics(metrics)
    (REPORTS / "findings.md").write_text(
        f"# Удержание и онбординг\n\n18 000 установок, 01.08–30.09.2026. Синтетические данные.\n\n"
        f"D30 доступен для {metrics['d30_eligible']:,} пользователей. "
        f"У завершивших онбординг D30={metrics['d30_onboarded']:.1%}, "
        f"у остальных {metrics['d30_not_onboarded']:.1%}; отношение {ratio:.2f}.\n\n"
        "Скрытая вовлечённость в генераторе влияет и на онбординг, и на возврат. "
        "Поэтому разрыв не является эффектом онбординга, даже после разбиения по каналам.\n\n"
        "Следующий шаг: A/B-тест упрощённого онбординга. Единица рандомизации — новая установка, "
        "основная метрика — D7, защитная — доля достигших ключевого действия. "
        "Анализ после полного окна D7, по назначенной группе (ITT).\n"
    )


if __name__ == "__main__":
    main()
