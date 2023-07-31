# display.py
import asyncio
from tabulate import tabulate
from gift_tracker import GiftTracker

async def display_table(gift_tracker):
    while True:
        # Display a table of the top ten gifters
        top_gifters = sorted(gift_tracker.gift_data.items(), key=lambda x: x[1], reverse=True)[:10]
        print(tabulate(top_gifters, headers=["User", "Number of Gifts"]))

        # Sleep for 30 seconds
        await asyncio.sleep(30)
