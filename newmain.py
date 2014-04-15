from SimoBot import SimoBot
import logging


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    simo = SimoBot("localhost", 6667, "SimoBot", ["#simobot"])
    simo.start()