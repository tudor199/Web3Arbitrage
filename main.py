
import argparse
import json

from manager.manager import Manager

from configurations import (
    models,
    abi
)
from secret import account


parser = argparse.ArgumentParser()

parser.add_argument('--network', '-n', default='polygon', choices=models.keys())
parser.add_argument('--preprocessing', '-p', required=False, default=False, action='store_true')

args = parser.parse_args()

model = models[args.network]

if args.preprocessing:
    Manager.generateState(abi, model, args.network)
else:
    f = open(f"state/{args.network}.json", "r")
    state = json.load(f)
    f.close()
    Manager(account, abi, state).start()
