from SimoBot import SimoBot
import logging

logging.basicConfig(level=logging.DEBUG)

simo = SimoBot("localhost", 6667, "SimoBot", ["#simobot"])
simo.start()