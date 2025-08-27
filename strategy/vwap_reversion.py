# strategy/vwap_reversion.py
import pandas as pd
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

    def _df_1m(self) -> pd.DataFrame:
        c = self.dc.get_1m_today(self.symbol)
        if not c: return pd.DataFrame()
        rows = [{"ts": utc_epoch_to_ist_dt(ts), "o": o, "h": h, "l": l, "c": cl, "v": v} for ts,o,h,l,cl,v in c]
        df = pd.DataFrame(rows)
        df = df[df['ts'].dt.time >= ORB_START_IST]
        cutoff = ist_now() - pd.Timedelta(minutes=self.lookback_min)
        return df[df['ts'] >= cutoff]

    def _vwap_bands(self, df: pd.DataFrame):
        tp = (df['h'] + df['l'] + df['c']) / 3.0
        pv = (tp * df['v']).cumsum()
        vv = (df['v']).cumsum().replace(0, pd.NA)
        vwap = (pv / vv).fillna(method='ffill')
        # use rolling std of close around vwap to build bands
        dev = (df['c'] - vwap).rolling(20).std()
        upper = vwap + self.k * dev
        lower = vwap - self.k * dev
        return vwap, upper, lower

    def signal(self, idx_ltp: float, rsi_val: Optional[float]) -> Optional[str]:
        df = self._df_1m()
        if df.empty or len(df) < 40:
            return None
        vwap, ub, lb = self._vwap_bands(df)
        if pd.isna(ub.iloc[-1]) or pd.isna(lb.iloc[-1]):
            return None
        last_c = df['c'].iloc[-1]
        last_ub = ub.iloc[-1]
        last_lb = lb.iloc[-1]

        # tag + reject: last close pierced band, current idx back inside
        try:
            ltp = self.dc.get_ltp(self.symbol)
        except Exception:
            ltp = last_c

        # prefer neutral RSI for reversion if available (but don't force it hard)
        if rsi_val is not None and (rsi_val < 40 or rsi_val > 60):
            return None

        if df['c'].iloc[-2] <= last_lb and ltp > last_lb:
            self.log("STRAT_SIG", reason=f"VWAPR CE: prev<=LB {last_lb:.2f} and LTP {ltp:.2f}>LB")
            return "CE"
        if df['c'].iloc[-2] >= last_ub and ltp < last_ub:
            self.log("STRAT_SIG", reason=f"VWAPR PE: prev>=UB {last_ub:.2f} and LTP {ltp:.2f}<UB")
            return "PE"
        return None
