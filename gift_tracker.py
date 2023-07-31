# gift_tracker.py
import pickle
import os
from collections import defaultdict

class GiftTracker:
    def __init__(self, pickle_file):
        self.pickle_file = pickle_file
        self.gift_data = self.load_gift_data()

    def load_gift_data(self):
        if os.path.exists(self.pickle_file):
            with open(self.pickle_file, 'rb') as f:
                return pickle.load(f)
        else:
            return defaultdict(int)

    def update_gift_data(self, user_id, gift_count):
        if user_id not in self.gift_data:
            self.gift_data[user_id] = 0
        self.gift_data[user_id] += gift_count
        with open(self.pickle_file, 'wb') as f:
            pickle.dump(self.gift_data, f)