import datetime as dt
import pytz

# --------- IDs ---------
CLIENT_ID = "YOUR_APP_ID"   # e.g., ABCD12345-100
TOKEN_PATH = "accessToken/token.txt"    # RAW v3 JWT only

# --------- Symbols ---------
INDEX_SYMBOL = "NSE:NIFTY50-INDEX"
EXPIRY_CODE  = "25AUG"      # update daily (e.g., 25AUG, 25SEP)

# --------- Time / Session ---------
IST = pytz.timezone("Asia/Kolkata")
ORB_START_IST = dt.time(9, 15)
ORB_END_IST   = dt.time(9, 30)
SQUARE_OFF_IST= dt.time(15, 20)

START_IMMEDIATELY = False            # off-hours testing
USE_YDAY_WHEN_TODAY_EMPTY = True    # off-hours testing

# --------- Trading / Risk ---------
LOT_SIZE                 = 75
ENTRY_BUFFER_PCT         = 0.05
COOLDOWN_SEC             = 60
MAX_CONCURRENT_POS       = 2
ALLOW_OPPOSITE_IF_SAFE   = True

MAX_DAILY_LOSS_INR       = 2000
COST_PER_SIDE_INR        = 20
INIT_SL_PCT              = 25
INIT_TP_PCT              = 40

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
RSI_PERIOD        = 14
RSI_TIMEFRAME_MIN = 5
RSI_LONG_MIN      = 55
RSI_SHORT_MAX     = 45

# --- BB Range Scalper (sideways mean reversion) ---
SCALP_ENABLED          = True     # master switch
SCALP_TP_PCT           = 7.0      # target on option premium (e.g., 5–10%)
SCALP_SL_PCT           = 8.0      # stop-loss on option premium
SCALP_MAX_HOLD_MIN     = 12       # time-based exit if no TP (minutes)
SCALP_COOLDOWN_SEC     = 120      # wait after a scalp exit before next scalp

# Signal settings
SCALP_BB_PERIOD        = 20       # Bollinger window (on 1m closes)
SCALP_BB_STD           = 2.0      # Band width
SCALP_RSI_MIN          = 40       # keep trades in "range" regime
SCALP_RSI_MAX          = 60
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
