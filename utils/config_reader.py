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

    A_MIN = config.get('General', 'A_MIN')
    A_MAX = config.get('General', 'A_MAX')
    B_MIN = config.get('General', 'B_MIN')
    B_MAX = config.get('General', 'B_MAX')
    C_MIN = config.get('General', 'C_MIN')
    C_MAX = config.get('General', 'C_MAX')
    
    return {
        'General': {
            'THICKNESS_EGG_SHELL_INTERVAL': THICKNESS_EGG_SHELL_INTERVAL,
            'SIZE_EGG_INTERVAL': SIZE_EGG_INTERVAL,
            'ROTATING_EGG_INTERVAL': ROTATING_EGG_INTERVAL,
            'A_MIN': A_MIN,
            'A_MAX': A_MAX,
            'B_MIN': B_MIN,
            'B_MAX': B_MAX,
            'C_MIN': C_MIN,
            'C_MAX': C_MAX
        }
    }