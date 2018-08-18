import argparse
import logging


def init_log():
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.DEBUG,format=FORMAT)

def parse_args():
    """parse argument"""
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--type')
    parser.add_argument('-p', '--port')
    parser.add_argument('-a', '--addr')
    parser.add_argument('-c', '--count', default=1)
    parser.add_argument('--flag')
    parser.add_argument('--file')
    parser.add_argument('--newfile')
    parser.add_argument('--build', action='store_true', default=False)
    parser.add_argument('--load', action='store_true', default=False)
    parser.add_argument('--filter', action='store_true', default=False)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-s', '--selfplay', action='store_true', default=False)

    args = parser.parse_args()

    return args