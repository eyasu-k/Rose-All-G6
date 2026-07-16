class Car:
    def __init__(self, info):
        self.x = info["x"]
        self.y = info["y"]
        self.sauce_active = info.get("sauce_active", False)
        self.sauce_hits_left = info.get("sauce_hits_left", 0)
