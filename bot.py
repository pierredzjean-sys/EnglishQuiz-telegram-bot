#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import random
from telegram import Bot

# ======================= CONFIG =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ex: "@moncanaledu" ou ID numérique -100...
DELAY_SECONDS = int(os.getenv("DELAY_SECONDS", "300"))
TEST_MODE = True
TEST
