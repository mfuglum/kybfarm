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
    #print(env)
    return env

def generate_config(template_path, config_path, env_file):
    # Read the template file and generate the config file
    with open(template_path, 'r') as file:
        file_contents = file.read()
        #print(file_contents)
        template = Template(file_contents)
        env = parse_environment_file(env_file)
        rendered_template = template.render(env)
    
        # Write the rendered template to the actual configuration file
        with open(config_path, 'w') as file:
            file.write(rendered_template)

def main():
    template_and_config_pairs = {
        "./homeassistant_templates/automations_template.yaml": "./server/homeassistant/config/automations.yaml",
        "./homeassistant_templates/configuration_template.yaml": "./server/homeassistant/config/configuration.yaml",
        "./homeassistant_templates/influxdb_template.yaml": "./server/homeassistant/config/influxdb.yaml",
        "./homeassistant_templates/input_select_template.yaml": "./server/homeassistant/config/input_select.yaml",
        "./homeassistant_templates/input_text_template.yaml": "./server/homeassistant/config/input_text.yaml",
        "./homeassistant_templates/input_boolean_template.yaml": "./server/homeassistant/config/input_boolean.yaml",
        "./homeassistant_templates/input_number_template.yaml": "./server/homeassistant/config/input_number.yaml",
        "./homeassistant_templates/input_datetime_template.yaml": "./server/homeassistant/config/input_datetime.yaml",
        "./appdaemon_templates/appdaemon_apps_template.yaml": "./server/appdaemon/config/apps/apps.yaml",
    }

    env_file = ".env"
    for template_path, config_path in template_and_config_pairs.items():

        generate_config(template_path, config_path, env_file)

if __name__ == "__main__":
    main()