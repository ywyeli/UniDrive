#!/bin/bash

set -e

cd ../scenario_runner

while IFS= read -r line; do
  python scenario_runner.py \
  --route srunner/data/routes_place3d.xml srunner/data/no_scenarios.json "$line" \
  --agent srunner/autoagents/npc_agent.py \
  --lidar-params ../hyperparams/base.toml \
  --hyperparams ../hyperparams/base.toml \
  --split training \
  --full_round &>> ../logs/base.out
done < ../scripts/place3d_routes.txt

cd ../scripts

