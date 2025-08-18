"""Motion commands for the Kestrel-1 rover."""

MAX_SPEED = 60


def move_forward(speed):
    return min(speed, MAX_SPEED)
