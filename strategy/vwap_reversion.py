# strategy/vwap_reversion.py
import pandas as pd, numpy as np
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
        if c is None: return pd.DataFrame()
        rows = []
        if isinstance(c, (list, tuple)):
            for row in c:
                if isinstance(row, dict):
                    ts = row.get("t") or row.get("ts")
                    o,h,l,cl,v = row.get("o"),row.get("h"),row.get("l"),row.get("c"),row.get("v")
                else:
                    if len(row) < 6: continue
                    ts,o,h,l,cl,v = row[:6]
                rows.append({"ts": utc_epoch_to_ist_dt(ts), "o":o, "h":h, "l":l, "c":cl, "v":v})
            df = pd.DataFrame(rows)
        elif isinstance(c, pd.DataFrame):
            df = c.copy()
            if "ts" not in df.columns:
                if "t" in df.columns:
                    df.rename(columns={"t":"ts"}, inplace=True)
                elif pd.api.types.is_datetime64_any_dtype(df.index):
                    df.reset_index(inplace=True)
                    df.rename(columns={df.columns[0]:"ts"}, inplace=True)
                else:
                    return pd.DataFrame()
            if not pd.api.types.is_datetime64_any_dtype(df["ts"]):
                df["ts"] = df["ts"].apply(utc_epoch_to_ist_dt)
        else:
            return pd.DataFrame()

        for col in ["o","h","l","c","v"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.dropna(subset=["o","h","l","c","v"], inplace=True)
        df.set_index("ts", inplace=True)
        return df.sort_index()

    def _df_1m(self) -> pd.DataFrame:
        df = self._as_df(self.dc.get_1m_today(self.symbol))
        if df.empty: return df
        df = df[df.index.time >= ORB_START_IST]
        cutoff = ist_now() - pd.Timedelta(minutes=self.lookback_min)
        return df[df.index >= cutoff]

    def _vwap_bands(self, df: pd.DataFrame):
        tp = (df["h"] + df["l"] + df["c"]) / 3.0
        pv = (tp * df["v"]).cumsum().astype(float)
        vv = df["v"].cumsum().astype(float)
        with np.errstate(divide="ignore", invalid="ignore"):
            vwap = np.where(vv > 0, pv / vv, np.nan)
        vwap = pd.Series(vwap, index=df.index, dtype="float64").ffill()
        dev = (df["c"].astype(float) - vwap).rolling(20, min_periods=10).std()
        return vwap, vwap + self.k * dev, vwap - self.k * dev

    def signal(self, idx_ltp: float, rsi_val: Optional[float]) -> Optional[str]:
        df = self._df_1m()
        if df.empty or len(df) < 40:
            return None
        vwap, ub, lb = self._vwap_bands(df)
        if any(pd.isna(x) for x in (vwap.iloc[-1], ub.iloc[-1], lb.iloc[-1])):
            return None

        last_c  = float(df["c"].iloc[-1])
        last_ub = float(ub.iloc[-1])
        last_lb = float(lb.iloc[-1])

        # Prefer neutral RSI for reversion (decisive range)
        if rsi_val is not None and (rsi_val < 40 or rsi_val > 60):
            return None

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
