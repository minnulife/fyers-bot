FyersBot/
├─ main.py                    # entrypoint
├─ config.py                  # all constants/knobs
├─ auth.py                    # build fyers client from token.txt
├─ data.py                    # data access: history/quotes, prev close, symbol resolver
├─ indicators.py              # RSI calc
├─ models.py                  # Position dataclass
├─ strategy/
│  └─ orb.py                  # ORB logic: levels, buffers, arming, entry checks
├─ engine.py                  # simulator engine (entries/exits, logging, summary)
├─ summary.py                 # EoD summary
├─ logging_utils.py           # CSV logger helpers
└─ token.txt                  # RAW v3 JWT (no APP_ID prefix)
