"""Obstacle detector for the Kestrel-1 camera."""
THRESHOLD_CM = 30
def detect(distance_cm):
    return distance_cm < THRESHOLD_CM
