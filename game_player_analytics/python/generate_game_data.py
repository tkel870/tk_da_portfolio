"""
Generate simulated live-service game telemetry + monetization data.

Outputs (created in ./data/raw):
- players.csv
- sessions.csv
- purchases.csv
- feature_flags.csv

Designed for portfolio use:
- Player-level dimension table
- Session telemetry table
- Purchase table
- Feature flag table (A/B test: Control vs Variant)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Settings (you can tweak later)
# -----------------------------
@dataclass
class Config:
    seed: int = 870  # wink to tkel870 🙂
    n_players: int = 1000
    start_date: date = date(2025, 10, 1)
    end_date: date = date(2026, 1, 31)

    # A/B test
    feature_name: str = "New_UI"
    variant_share: float = 0.5  # 50/50 split

    # Output path
    out_dir: str = os.path.join("data", "raw")


CFG = Config()


# -----------------------------
# Helper functions
# -----------------------------
def ensure_out_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def daterange(start: date, end: date) -> List[date]:
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]


def weighted_choice(rng: np.random.Generator, items: List[str], weights: List[float], size: int) -> np.ndarray:
    w = np.array(weights, dtype=float)
    w = w / w.sum()
    return rng.choice(items, size=size, p=w)


def clamp_int(x: float, lo: int, hi: int) -> int:
    return int(max(lo, min(hi, round(x))))


# -----------------------------
# Data generation
# -----------------------------
def generate_players(rng: np.random.Generator) -> pd.DataFrame:
    player_ids = [f"P{str(i).zfill(5)}" for i in range(1, CFG.n_players + 1)]

    all_days = daterange(CFG.start_date, CFG.end_date)
    # more signups earlier than later (common in launches)
    signup_weights = np.linspace(1.4, 0.8, num=len(all_days))
    signup_weights = signup_weights / signup_weights.sum()
    signup_dates = rng.choice(all_days, size=CFG.n_players, p=signup_weights)

    regions = weighted_choice(rng, ["NA", "EU", "APAC"], [0.52, 0.30, 0.18], CFG.n_players)
    platforms = weighted_choice(rng, ["PC", "Console"], [0.62, 0.38], CFG.n_players)
    channels = weighted_choice(rng, ["Organic", "Paid", "Influencer"], [0.55, 0.30, 0.15], CFG.n_players)

    players = pd.DataFrame(
        {
            "player_id": player_ids,
            "signup_date": pd.to_datetime(signup_dates),
            "region": regions,
            "platform": platforms,
            "acquisition_channel": channels,
        }
    )
    players["signup_date"] = players["signup_date"].dt.date
    return players


def generate_feature_flags(rng: np.random.Generator, players: pd.DataFrame) -> pd.DataFrame:
    test_groups = rng.choice(
        ["Control", "Variant"],
        size=len(players),
        p=[1 - CFG.variant_share, CFG.variant_share],
    )
    flags = pd.DataFrame(
        {
            "player_id": players["player_id"].values,
            "test_group": test_groups,
            "feature_name": CFG.feature_name,
        }
    )
    return flags


def generate_sessions_and_purchases(
    rng: np.random.Generator,
    players: pd.DataFrame,
    flags: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    We simulate:
    - Retention decay: players become less likely to play as days since signup increases.
    - Engagement patterns differ by platform and test_group.
    - Purchases occur with probability correlated with engagement + slight uplift for Variant.
    """
    # Quick lookup: player -> test_group
    test_group_map = dict(zip(flags["player_id"], flags["test_group"]))

    sessions_rows = []
    purchases_rows = []

    session_counter = 1
    purchase_counter = 1

    # baseline tendencies by platform/channel
    platform_session_mult = {"PC": 1.0, "Console": 0.92}
    channel_retention_mult = {"Organic": 1.05, "Paid": 0.98, "Influencer": 1.02}

    for _, row in players.iterrows():
        pid = row["player_id"]
        signup = row["signup_date"]
        platform = row["platform"]
        channel = row["acquisition_channel"]
        group = test_group_map[pid]

        # A/B uplift: Variant players retain slightly better & engage slightly more
        group_retention_mult = 1.06 if group == "Variant" else 1.00
        group_engagement_mult = 1.04 if group == "Variant" else 1.00

        # player "skill/interest" factor
        player_affinity = rng.lognormal(mean=0.0, sigma=0.35)  # >1 = more engaged
        # player's typical session length baseline
        base_session_len = rng.normal(loc=32, scale=10) * group_engagement_mult
        base_session_len = max(8, base_session_len)

        # how long they "stick around" (caps total active window)
        max_active_days = clamp_int(rng.normal(loc=35, scale=18) * group_retention_mult, 5, 120)

        # generate activity day by day
        end_active = min(CFG.end_date, signup + timedelta(days=max_active_days))

        # we bias against sessions too close to end_date beyond active window
        active_days = daterange(signup, end_active)

        for d in active_days:
            days_since_signup = (d - signup).days

            # retention probability decays over time (fast early drop-off)
            # This yields realistic D1/D7/D30 retention patterns.
            decay = np.exp(-days_since_signup / 18.0)  # slower decay = better retention
            play_prob = 0.42 * decay

            # modifiers
            play_prob *= platform_session_mult[platform]
            play_prob *= channel_retention_mult[channel]
            play_prob *= group_retention_mult
            play_prob *= min(1.35, player_affinity)

            play_prob = float(np.clip(play_prob, 0.02, 0.75))

            if rng.random() < play_prob:
                # sessions per day: 1, occasionally 2+
                sessions_today = 1
                if rng.random() < (0.12 * group_engagement_mult * min(1.2, player_affinity)):
                    sessions_today += 1
                if rng.random() < 0.03:
                    sessions_today += 1

                for _ in range(sessions_today):
                    session_id = f"S{str(session_counter).zfill(7)}"
                    session_counter += 1

                    # session length and levels completed correlate loosely
                    session_length = rng.normal(loc=base_session_len, scale=9)
                    session_length *= min(1.4, player_affinity)
                    session_length = clamp_int(session_length, 5, 180)

                    levels_completed = clamp_int(rng.normal(loc=session_length / 12, scale=1.2), 0, 20)

                    sessions_rows.append(
                        {
                            "session_id": session_id,
                            "player_id": pid,
                            "session_date": d,
                            "session_length_min": session_length,
                            "levels_completed": levels_completed,
                        }
                    )

                    # Purchase probability: influenced by session length + slight uplift for Variant
                    # purchases are rarer than sessions, like real games.
                    base_purchase_prob = 0.015 + (session_length / 3000.0)
                    if group == "Variant":
                        base_purchase_prob *= 1.10  # A/B uplift

                    # whales exist (rare but real)
                    whale_factor = 1.0
                    if rng.random() < 0.03:
                        whale_factor = 2.2

                    purchase_prob = float(np.clip(base_purchase_prob * whale_factor, 0.0, 0.12))

                    if rng.random() < purchase_prob:
                        purchase_id = f"PU{str(purchase_counter).zfill(7)}"
                        purchase_counter += 1

                        item_type = rng.choice(["Cosmetic", "Boost"], p=[0.72, 0.28])
                        # revenue distribution: mostly small, sometimes medium, rarely high
                        if item_type == "Cosmetic":
                            revenue = rng.choice([2.99, 4.99, 9.99, 14.99, 19.99], p=[0.28, 0.32, 0.24, 0.12, 0.04])
                        else:
                            revenue = rng.choice([0.99, 1.99, 3.99, 7.99, 12.99], p=[0.25, 0.30, 0.25, 0.15, 0.05])

                        # whales can buy bigger items
                        if whale_factor > 1.0 and rng.random() < 0.25:
                            revenue *= rng.choice([2, 3], p=[0.7, 0.3])

                        purchases_rows.append(
                            {
                                "purchase_id": purchase_id,
                                "player_id": pid,
                                "purchase_date": d,
                                "revenue": float(round(revenue, 2)),
                                "item_type": item_type,
                            }
                        )

    sessions = pd.DataFrame(sessions_rows)
    purchases = pd.DataFrame(purchases_rows)

    # Ensure datatypes are clean
    if not sessions.empty:
        sessions["session_date"] = pd.to_datetime(sessions["session_date"]).dt.date
        sessions["session_length_min"] = sessions["session_length_min"].astype(int)
        sessions["levels_completed"] = sessions["levels_completed"].astype(int)

    if not purchases.empty:
        purchases["purchase_date"] = pd.to_datetime(purchases["purchase_date"]).dt.date
        purchases["revenue"] = purchases["revenue"].astype(float)

    return sessions, purchases


def main() -> None:
    rng = np.random.default_rng(CFG.seed)
    ensure_out_dir(CFG.out_dir)

    players = generate_players(rng)
    flags = generate_feature_flags(rng, players)
    sessions, purchases = generate_sessions_and_purchases(rng, players, flags)

    # Save CSVs
    players.to_csv(os.path.join(CFG.out_dir, "players.csv"), index=False)
    flags.to_csv(os.path.join(CFG.out_dir, "feature_flags.csv"), index=False)
    sessions.to_csv(os.path.join(CFG.out_dir, "sessions.csv"), index=False)
    purchases.to_csv(os.path.join(CFG.out_dir, "purchases.csv"), index=False)

    # Tiny summary printout (so you know it worked)
    print("✅ Data generated!")
    print(f"players:        {len(players):,}")
    print(f"feature_flags:  {len(flags):,}")
    print(f"sessions:       {len(sessions):,}")
    print(f"purchases:      {len(purchases):,}")
    print(f"Saved to:       {CFG.out_dir}/")

def main() -> None:
    import os
    import numpy as np
    import pandas as pd
    from datetime import date

    print("Starting data generation...")

    # ----- Settings -----
    seed = 870
    n_players = 1000
    start_date = date(2025, 10, 1)
    end_date = date(2026, 1, 31)
    feature_name = "New_UI"
    variant_share = 0.5

    out_dir = os.path.join("data", "raw")
    os.makedirs(out_dir, exist_ok=True)

    rng = np.random.default_rng(seed)

    # ----- Create players -----
    player_ids = [f"P{str(i).zfill(5)}" for i in range(1, n_players + 1)]
    all_days = pd.date_range(start_date, end_date, freq="D").date

    # more signups early
    weights = np.linspace(1.4, 0.8, num=len(all_days))
    weights = weights / weights.sum()
    signup_dates = rng.choice(all_days, size=n_players, p=weights)

    def wchoice(items, probs, size):
        return rng.choice(items, size=size, p=np.array(probs) / np.sum(probs))

    players = pd.DataFrame(
        {
            "player_id": player_ids,
            "signup_date": signup_dates,
            "region": wchoice(["NA", "EU", "APAC"], [0.52, 0.30, 0.18], n_players),
            "platform": wchoice(["PC", "Console"], [0.62, 0.38], n_players),
            "acquisition_channel": wchoice(["Organic", "Paid", "Influencer"], [0.55, 0.30, 0.15], n_players),
        }
    )

    # ----- Feature flags (A/B test) -----
    flags = pd.DataFrame(
        {
            "player_id": players["player_id"],
            "test_group": rng.choice(["Control", "Variant"], size=n_players, p=[1 - variant_share, variant_share]),
            "feature_name": feature_name,
        }
    )
    group_map = dict(zip(flags["player_id"], flags["test_group"]))

    # ----- Sessions + purchases -----
    sessions_rows = []
    purchases_rows = []
    session_counter = 1
    purchase_counter = 1

    platform_mult = {"PC": 1.0, "Console": 0.92}
    channel_mult = {"Organic": 1.05, "Paid": 0.98, "Influencer": 1.02}

    for _, pr in players.iterrows():
        pid = pr["player_id"]
        signup = pr["signup_date"]
        platform = pr["platform"]
        channel = pr["acquisition_channel"]
        group = group_map[pid]

        group_ret_mult = 1.06 if group == "Variant" else 1.00
        group_eng_mult = 1.04 if group == "Variant" else 1.00

        affinity = float(rng.lognormal(mean=0.0, sigma=0.35))
        base_len = max(8, float(rng.normal(loc=32, scale=10)) * group_eng_mult)

        max_active_days = int(np.clip(rng.normal(loc=35, scale=18) * group_ret_mult, 5, 120))
        active_end = min(end_date, (pd.to_datetime(signup) + pd.Timedelta(days=max_active_days)).date())

        active_days = pd.date_range(signup, active_end, freq="D").date

        for d in active_days:
            days_since = (pd.to_datetime(d) - pd.to_datetime(signup)).days
            decay = float(np.exp(-days_since / 18.0))
            play_prob = 0.42 * decay
            play_prob *= platform_mult[platform]
            play_prob *= channel_mult[channel]
            play_prob *= group_ret_mult
            play_prob *= min(1.35, affinity)
            play_prob = float(np.clip(play_prob, 0.02, 0.75))

            if rng.random() < play_prob:
                sessions_today = 1
                if rng.random() < (0.12 * group_eng_mult * min(1.2, affinity)):
                    sessions_today += 1
                if rng.random() < 0.03:
                    sessions_today += 1

                for _ in range(sessions_today):
                    sid = f"S{str(session_counter).zfill(7)}"
                    session_counter += 1

                    s_len = float(rng.normal(loc=base_len, scale=9)) * min(1.4, affinity)
                    s_len = int(np.clip(round(s_len), 5, 180))
                    levels = int(np.clip(round(rng.normal(loc=s_len / 12, scale=1.2)), 0, 20))

                    sessions_rows.append(
                        {
                            "session_id": sid,
                            "player_id": pid,
                            "session_date": d,
                            "session_length_min": s_len,
                            "levels_completed": levels,
                        }
                    )

                    # purchase probability
                    base_p = 0.015 + (s_len / 3000.0)
                    if group == "Variant":
                        base_p *= 1.10

                    whale = 2.2 if rng.random() < 0.03 else 1.0
                    p_prob = float(np.clip(base_p * whale, 0.0, 0.12))

                    if rng.random() < p_prob:
                        puid = f"PU{str(purchase_counter).zfill(7)}"
                        purchase_counter += 1

                        item_type = rng.choice(["Cosmetic", "Boost"], p=[0.72, 0.28])
                        if item_type == "Cosmetic":
                            revenue = float(rng.choice([2.99, 4.99, 9.99, 14.99, 19.99], p=[0.28, 0.32, 0.24, 0.12, 0.04]))
                        else:
                            revenue = float(rng.choice([0.99, 1.99, 3.99, 7.99, 12.99], p=[0.25, 0.30, 0.25, 0.15, 0.05]))

                        if whale > 1.0 and rng.random() < 0.25:
                            revenue *= float(rng.choice([2, 3], p=[0.7, 0.3]))

                        purchases_rows.append(
                            {
                                "purchase_id": puid,
                                "player_id": pid,
                                "purchase_date": d,
                                "revenue": round(revenue, 2),
                                "item_type": item_type,
                            }
                        )

    sessions = pd.DataFrame(sessions_rows)
    purchases = pd.DataFrame(purchases_rows)

    # ----- Save CSVs -----
    players.to_csv(os.path.join(out_dir, "players.csv"), index=False)
    flags.to_csv(os.path.join(out_dir, "feature_flags.csv"), index=False)
    sessions.to_csv(os.path.join(out_dir, "sessions.csv"), index=False)
    purchases.to_csv(os.path.join(out_dir, "purchases.csv"), index=False)

    print("✅ Data generated!")
    print(f"players:        {len(players):,}")
    print(f"feature_flags:  {len(flags):,}")
    print(f"sessions:       {len(sessions):,}")
    print(f"purchases:      {len(purchases):,}")
    print(f"Saved to:       {out_dir}/")


if __name__ == "__main__":
    main()
