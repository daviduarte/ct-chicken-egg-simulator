import configparser


def read_config(file_path):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    
    # Read the configuration file
    config.read(file_path)
    
    # Access values from the sections
    THICKNESS_EGG_SHELL_INTERVAL = config.get('General', 'THICKNESS_EGG_SHELL_INTERVAL')
    SIZE_EGG_INTERVAL = config.get('General', 'SIZE_EGG_INTERVAL')
    ROTATING_EGG_INTERVAL = config.get('General', 'ROTATING_EGG_INTERVAL')
    
    return {
        'General': {
            'THICKNESS_EGG_SHELL_INTERVAL': THICKNESS_EGG_SHELL_INTERVAL,
            'SIZE_EGG_INTERVAL': SIZE_EGG_INTERVAL,
            'ROTATING_EGG_INTERVAL': ROTATING_EGG_INTERVAL
        }
    }