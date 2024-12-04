from collections import defaultdict
latest_messages = defaultdict(lambda: None)
latest_messages[123] = 123
latest_messages[12333] = 123
print(list(latest_messages.values()))