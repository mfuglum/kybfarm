import os
from jinja2 import Template

def parse_environment_file(env_file):
    env = {}
    with open(env_file, 'r') as file:
        env_file = file.read()
        for pair in env_file.split("\n"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                env[key.strip()] = value.strip()
    print(env)
    return env

def generate_config(template_path, config_path, env_file):
    # Read the template file and generate the config file
    with open(template_path, 'r') as file:
        file_contents = file.read()
        template = Template(file_contents)
        env = parse_environment_file(env_file)
        rendered_template = template.render(env)
    
        # Write the rendered template to the actual configuration file
        with open(config_path, 'w') as file:
            file.write(rendered_template)

def main():
    template_and_config_pairs = {
        "./automations_template.yaml": "./server/homeassistant/config/automations.yaml",
        "./configuration_template.yaml": "./server/homeassistant/config/configuration.yaml",
        "./influxdb_template.yaml": "./server/homeassistant/config/influxdb.yaml",
        "./input_select_template.json": "./server/homeassistant/config/.storage/input_select",
        "./input_text_template.json": "./server/homeassistant/config/.storage/input_text",
        "./input_boolean_template.json": "./server/homeassistant/config/.storage/input_boolean",
    }

    env_file = ".env"
    for template_path, config_path in template_and_config_pairs.items():
        generate_config(template_path, config_path, env_file)

if __name__ == "__main__":
    main()