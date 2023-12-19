import logging
import logging.config
import yaml
import os

FILE_PATH = os.path.abspath(__file__)
CWD = os.path.dirname(FILE_PATH)
os.chdir(CWD)


def get_logger(logger:str = 'development', log_filename:str = None):
    
    with open('../config.yaml', 'rt') as f:
        config = yaml.safe_load(f.read())

    config = config['logger']
    logger = logger.replace('foreclosure_suite.', '')
    
    if log_filename and 'file' in config['loggers'][logger]['handlers']:
        config['handlers']['file'].update({
            'filename': log_filename
        })

    logging.config.dictConfig(config)

    return logging.getLogger(logger)

if __name__ == '__main__':
    logger = get_logger('development', log_filename='test.log')
    logger.info('this is a test of the logger')