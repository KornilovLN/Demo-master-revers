#!/usr/bin/env python3

import yaml

def load_commands(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def run_command(command_id, commands):
    for command in commands['commands']:
        if command['id'] == command_id:
            print(f"Running command: {command['description']}")
            for step in command['steps']:
                print(f"Step: {step['name']}")
                print(f"Action: {step['action']}")
            return
    print(f"Command {command_id} not found.")

if __name__ == "__main__":
    commands = load_commands('commands.yaml')
    run_command('explain_project_structure', commands)
