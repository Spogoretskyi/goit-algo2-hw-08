import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.users = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id in self.users:
            history = self.users[user_id]
            while history and history[0] <= current_time - self.window_size:
                history.popleft()

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.users:
            self.users[user_id] = deque()

        if len(self.users[user_id]) < self.max_requests:
            return True
        else:
            return False

    def record_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.users:
            self.users[user_id] = deque()

        if len(self.users[user_id]) < self.max_requests:
            self.users[user_id].append(current_time)
            return True
        else:
            return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id in self.users and len(self.users[user_id]) >= self.max_requests:
            first_request_time = self.users[user_id][0]
            return max(0, (first_request_time + self.window_size) - current_time)
        else:
            return 0


class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.users_last_message_time = {}

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()

        if user_id in self.users_last_message_time:
            last_message_time = self.users_last_message_time[user_id]

            if current_time - last_message_time < self.min_interval:
                return False
        return True

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            current_time = time.time()
            self.users_last_message_time[user_id] = current_time
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()

        if user_id in self.users_last_message_time:
            last_message_time = self.users_last_message_time[user_id]
            remaining_time = self.min_interval - (current_time - last_message_time)
            return max(0, remaining_time)

        return 0
