# strategy/supertrend_trend.py
import pandas as pd
from typing import Optional
from strategy.base import IStrategy
from data import utc_epoch_to_ist_dt
from config import ORB_START_IST, RSI_LONG_MIN, RSI_SHORT_MAX

def atr(df: pd.DataFrame, period=10):
    hl = df["h"] - df["l"]
    hc = (df["h"] - df["c"].shift()).abs()
    lc = (df["l"] - df["c"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=max(2, period//2)).mean()

def supertrend(df: pd.DataFrame, period=10, multiplier=3.0):
    _atr = atr(df, period)
    hl2 = (df["h"] + df["l"]) / 2.0
    upper = hl2 + multiplier * _atr
    lower = hl2 - multiplier * _atr

    st = pd.Series(index=df.index, dtype=float)
    dir_up = True
    for i in range(len(df)):
        if i == 0:
            st.iloc[i] = upper.iloc[i]
            dir_up = df["c"].iloc[i] >= st.iloc[i]
            continue
        if dir_up:
            st.iloc[i] = min(upper.iloc[i], st.iloc[i-1])
            if df["c"].iloc[i] < st.iloc[i]:
                dir_up = False
                st.iloc[i] = lower.iloc[i]
        else:
            st.iloc[i] = max(lower.iloc[i], st.iloc[i-1])
            if df["c"].iloc[i] > st.iloc[i]:
                dir_up = True
                st.iloc[i] = upper.iloc[i]
    return st, dir_up

class SupertrendTrend(IStrategy):
    name = "supertrend_trend"

    def __init__(self, data_client, logger, index_symbol: str, period=10, multiplier=3.0, tf_min=5):
        self.dc = data_client
        self.log = logger
        self.symbol = index_symbol
        self.period = period
        self.multiplier = multiplier
        self.tf_min = tf_min

    def _as_df(self, c) -> pd.DataFrame:
        if c is None:
            return pd.DataFrame()

        if isinstance(c, (list, tuple)):
            rows = []
            for row in c:
                if isinstance(row, dict):
                    ts = row.get("t") or row.get("ts")
                    o = row.get("o"); h = row.get("h"); l = row.get("l"); cl = row.get("c"); v = row.get("v")
                else:
                    if len(row) < 6:
                        continue
                    ts, o, h, l, cl, v = row[:6]
                rows.append({"ts": utc_epoch_to_ist_dt(ts), "o": o, "h": h, "l": l, "c": cl, "v": v})
            df = pd.DataFrame(rows)
        elif isinstance(c, pd.DataFrame):
            df = c.copy()
            if "ts" not in df.columns:
                if "t" in df.columns:
                    df = df.rename(columns={"t": "ts"})
                elif pd.api.types.is_datetime64_any_dtype(df.index):
                    df = df.reset_index().rename(columns={df.columns[0]: "ts"})
                else:
                    return pd.DataFrame()
            if not pd.api.types.is_datetime64_any_dtype(df["ts"]):
                df["ts"] = df["ts"].apply(utc_epoch_to_ist_dt)
        else:
            return pd.DataFrame()

        if df.empty or "ts" not in df.columns:
            return pd.DataFrame()

        for col in ["o", "h", "l", "c", "v"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["o", "h", "l", "c", "v"])
        df = df.set_index("ts").sort_index()
        return df

    def _df_agg(self) -> pd.DataFrame:
        c = self.dc.get_1m_today(self.symbol)
        df = self._as_df(c)
        if df.empty:
            return df
        df = df[df.index.time >= ORB_START_IST]
        # resample on index (no 'on' kw)
        o = df["o"].resample(f"{self.tf_min}min").first()
        h = df["h"].resample(f"{self.tf_min}min").max()
        l = df["l"].resample(f"{self.tf_min}min").min()
        cl = df["c"].resample(f"{self.tf_min}min").last()
        out = pd.DataFrame({"o": o, "h": h, "l": l, "c": cl}).dropna()
        return out

    def signal(self, idx_ltp: float, rsi_val: Optional[float]) -> Optional[str]:
        df5 = self._df_agg()
        if df5.empty or len(df5) < max(14, self.period + 5):
            return None

        st, _ = supertrend(df5, period=self.period, multiplier=self.multiplier)
        last_st = float(st.iloc[-1])
        last_c  = float(df5["c"].iloc[-1])

        if rsi_val is None:
            return None

        # Trend-follow with RSI confirmation
        if last_c > last_st and rsi_val > RSI_LONG_MIN:
            self.log("STRAT_SIG", reason=f"ST up: c>{last_st:.2f} RSI={rsi_val:.1f} -> CE")
            return "CE"
        if last_c < last_st and rsi_val < RSI_SHORT_MAX:
            self.log("STRAT_SIG", reason=f"ST down: c<{last_st:.2f} RSI={rsi_val:.1f} -> PE")
            return "PE"
        return None
