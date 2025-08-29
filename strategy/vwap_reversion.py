# strategy/vwap_reversion.py
import pandas as pd
import numpy as np
from typing import Optional
from strategy.base import IStrategy
from data import utc_epoch_to_ist_dt, ist_now
from config import ORB_START_IST

class VWAPReversion(IStrategy):
    name = "vwap_reversion"

    def __init__(self, data_client, logger, index_symbol: str, band_k=2.0, lookback_min=120):
        self.dc = data_client
        self.log = logger
        self.symbol = index_symbol
        self.k = band_k
        self.lookback_min = lookback_min

    def _as_df(self, c) -> pd.DataFrame:
        """
        Normalize candles into a tz-aware IST-indexed DataFrame with columns: o,h,l,c,v.
        Accepts: list of [epoch,o,h,l,c,v], list of dicts, or a DataFrame.
        """
        if c is None:
            return pd.DataFrame()

        # List-like candles
        if isinstance(c, (list, tuple)):
            rows = []
            for row in c:
                # [ts, o, h, l, c, v] or dict-like
                if isinstance(row, dict):
                    ts = row.get("t") or row.get("ts")
                    o = row.get("o"); h = row.get("h"); l = row.get("l"); cl = row.get("c"); v = row.get("v")
                else:
                    if len(row) < 6:
                        continue
                    ts, o, h, l, cl, v = row[:6]
                rows.append({"ts": utc_epoch_to_ist_dt(ts), "o": o, "h": h, "l": l, "c": cl, "v": v})
            df = pd.DataFrame(rows)

        # Already a DataFrame
        elif isinstance(c, pd.DataFrame):
            df = c.copy()
            # try to find timestamp
            if "ts" not in df.columns:
                if "t" in df.columns:
                    df = df.rename(columns={"t": "ts"})
                elif df.index.name in (None, "", "ts"):
                    # if index is datetime, promote to 'ts'
                    if pd.api.types.is_datetime64_any_dtype(df.index):
                        df = df.reset_index().rename(columns={df.columns[0]: "ts"})
                    else:
                        # can't find ts; bail
                        return pd.DataFrame()
            # ensure datetime tz-aware
            if not pd.api.types.is_datetime64_any_dtype(df["ts"]):
                # assume epoch seconds
                df["ts"] = df["ts"].apply(utc_epoch_to_ist_dt)
        else:
            return pd.DataFrame()

        if df.empty or "ts" not in df.columns:
            return pd.DataFrame()

        # force numeric
        for col in ["o", "h", "l", "c", "v"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["o", "h", "l", "c", "v"])

        # set index, sort
        df = df.set_index("ts").sort_index()
        return df

    def _df_1m(self) -> pd.DataFrame:
        c = self.dc.get_1m_today(self.symbol)
        df = self._as_df(c)
        if df.empty:
            return df
        # post-open only
        df = df[df.index.time >= ORB_START_IST]
        # recent window
        cutoff = ist_now() - pd.Timedelta(minutes=self.lookback_min)
        df = df[df.index >= cutoff]
        return df

    def _vwap_bands(self, df: pd.DataFrame):
        tp = (df["h"] + df["l"] + df["c"]) / 3.0
        pv = (tp * df["v"]).cumsum().astype(float)
        vv = df["v"].cumsum().astype(float)
        with np.errstate(divide="ignore", invalid="ignore"):
            vwap = np.where(vv > 0, pv / vv, np.nan)
        vwap = pd.Series(vwap, index=df.index, dtype="float64").ffill()
        diff = (df["c"].astype(float) - vwap)
        dev = diff.rolling(window=20, min_periods=10).std()
        upper = vwap + self.k * dev
        lower = vwap - self.k * dev
        return vwap, upper, lower

    def signal(self, idx_ltp: float, rsi_val: Optional[float]) -> Optional[str]:
        df = self._df_1m()
        if df.empty or len(df) < 40:
            return None

        vwap, ub, lb = self._vwap_bands(df)
        if any(pd.isna(x) for x in (vwap.iloc[-1], ub.iloc[-1], lb.iloc[-1])):
            return None

        last_c = float(df["c"].iloc[-1])
        last_ub = float(ub.iloc[-1])
        last_lb = float(lb.iloc[-1])

        # prefer neutral RSI (range conditions)
        if rsi_val is not None and (rsi_val < 40 or rsi_val > 60):
            return None

        # live LTP (fallback)
        try:
            ltp = float(self.dc.get_ltp(self.symbol))
        except Exception:
            ltp = last_c

        prev_close = float(df["c"].iloc[-2]) if len(df) >= 2 else last_c

        if prev_close <= last_lb and ltp > last_lb:
            self.log("STRAT_SIG", reason=f"VWAPR CE: prev<=LB {last_lb:.2f} & LTP {ltp:.2f}>LB")
            return "CE"
        if prev_close >= last_ub and ltp < last_ub:
            self.log("STRAT_SIG", reason=f"VWAPR PE: prev>=UB {last_ub:.2f} & LTP {ltp:.2f}<UB")
            return "PE"

        return None
