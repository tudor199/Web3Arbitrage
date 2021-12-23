
import argparse

from manager.manager import Manager

from configurations import (
    models,
    abi
)
from secret import account


parser = argparse.ArgumentParser()

parser.add_argument('--model', '-m', default='matic', choices=['matic'])

args = parser.parse_args()

model = models[args.model]
Manager(account, abi, model).start()


