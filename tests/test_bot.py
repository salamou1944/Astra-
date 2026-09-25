import os,unittest
from unittest.mock import patch
from decimal import Decimal
from scripts.astra_bot import run_once

from astra.core import Bar

class BotTests(unittest.TestCase):
    def test_paper_entry(self):
        bars=[Bar(i,100+i) for i in range(40)]
        with patch("scripts.astra_bot.fetch_ohlc",return_value=bars):
            d=run_once(previous_signal=0,quantity=Decimal("0.001"))
        self.assertEqual(d["mode"],"PAPER")
        self.assertFalse(d["live_order_submitted"])
        self.assertEqual(d["paper_position"],"0.001")

    def test_live_env_cannot_run(self):
        with patch.dict(os.environ,{"ASTRA_LIVE_TRADING":"1"}):
            with self.assertRaises(SystemExit):
                import scripts.astra_bot as b
                b.main()
