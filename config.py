import datetime as dt
import pytz

START_IMMEDIATELY = False            # off-hours testing
USE_YDAY_WHEN_TODAY_EMPTY = True    # off-hours testing

# --------- IDs ---------
CLIENT_ID = "YOUR_APP_ID"   # e.g., ABCD12345-100
TOKEN_PATH = "accessToken/token.txt"    # RAW v3 JWT only

# --------- Symbols ---------
INDEX_SYMBOL = "NSE:NIFTY50-INDEX"
EXPIRY_CODE  = "30SEP"      # update daily (e.g., 25AUG, 25SEP)

# --------- Time / Session ---------
IST = pytz.timezone("Asia/Kolkata")
ORB_START_IST = dt.time(9, 15)
ORB_END_IST   = dt.time(9, 30)
SQUARE_OFF_IST= dt.time(15, 20)


# --------- Trading / Risk ---------
LOT_SIZE                 = 75
ENTRY_BUFFER_PCT         = 0.05
COOLDOWN_SEC             = 60
MAX_CONCURRENT_POS       = 2
ALLOW_OPPOSITE_IF_SAFE   = True

MAX_DAILY_LOSS_INR       = 2000
COST_PER_SIDE_INR        = 20
INIT_SL_PCT              = 20
INIT_TP_PCT              = 25

TRAIL_STEPS = [
    (10,  -5),
    (20,   0),
    (30, +10),
    (40, +20),
]
DD_HARD_DROP_PCT  = 8.0

TIME_BASED_EXIT_MIN   = 30
MOMENTUM_FAST_MIN     = 5
SLOW_PROFIT_PCT       = 15
REDUCED_TP_PCT        = 25

USE_PROJECTED_RISK_BLOCK = True

# --------- RSI ---------
USE_RSI           = True
RSI_PERIOD        = 10
RSI_TIMEFRAME_MIN = 3
RSI_LONG_MIN      = 55
RSI_SHORT_MAX     = 45

# --- BB Range Scalper (sideways mean reversion) ---
SCALP_ENABLED          = True     # master switch
SCALP_TP_PCT           = 6.5      # target on option premium (e.g., 5–10%)
SCALP_SL_PCT           = 8.0      # stop-loss on option premium
SCALP_MAX_HOLD_MIN     = 10       # time-based exit if no TP (minutes)
SCALP_COOLDOWN_SEC     = 120      # wait after a scalp exit before next scalp

# Signal settings
SCALP_BB_PERIOD        = 20       # Bollinger window (on 1m closes)
SCALP_BB_STD           = 2.0      # Band width
SCALP_RSI_MIN          = 45       # keep trades in "range" regime
SCALP_RSI_MAX          = 55
SCALP_LOOKBACK_MIN     = 90       # minutes of 1m data to compute BB/RSI



# --------- Re-entry guards ---------
PREVENT_DUPLICATE_SIDE = True
REARM_ON_PULLBACK      = True
REARM_PULLBACK_PCT     = 0.02
REARM_USING_OR_BAND    = False

# --------- Logging ---------
LOG_DIR = "logs"

# --- Snapshots & diagnostics ---
SNAPSHOT_INTERVAL_SEC   = 15 * 60   # 15 minutes
ENABLE_DIAGNOSTICS      = True      # log why entries were not taken
ENABLE_MOMENTUM_LOGS    = True      # log RSI regime & price-zone shifts
RSI_HYSTERESIS          = 1.0       # RSI points to reduce flip-flop around thresholds

# --- Diagnostics throttling ---
DIAG_INTERVAL_SEC       = 15 * 60   # minimum seconds between DIAG_NO_ENTRY logs
DIAG_ONLY_ON_CHANGE     = True      # log only if the reason set changed vs last time

REARM_USING_OR_BAND = True


# --- Drawdown (separate for core vs scalp) ---
CORE_DD_HARD_DROP_PCT = 10.0
SCALP_DD_HARD_DROP_PCT = 8.0
CORE_MIN_PEAK_GAIN_BEFORE_DD_PCT = 12.0   # require +12% over entry before DD triggers (core)
SCALP_MIN_PEAK_GAIN_BEFORE_DD_PCT = 6.0   # require +6% over entry before DD triggers (scalp)

# --- Breakeven stop (when trade goes your way) ---
BREAKEVEN_AT_PROFIT_PCT = 10.0   # when premium gain ≥ 10%, move SL to ~breakeven
BREAKEVEN_OFFSET_PCT    = 0.5    # keep tiny cushion (0.5% above EP)

# --- Scalp stacking guard ---
SCALP_MAX_OPEN             = 1   # max simultaneous scalp positions
SCALP_MAX_PER_SIDE         = 1   # at most 1 scalp per side (CE/PE)
SCALP_ENTRY_MIN_GAP_SEC    = 180 # min seconds between any two scalp entries
