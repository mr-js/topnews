from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
import uuid
import webbrowser
import os
import logging


from target import Target


DEBUG_LEVEL = logging.INFO
##logging.basicConfig(handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join('logs', 'topnews.log'), 'w', 'utf-8')], level=DEBUG_LEVEL, format='%(asctime)s - %(levelname)s: %(module)s, %(lineno)s, %(funcName)s - %(message)s', datefmt='%d.%m.%y %H:%M:%S')
logging.basicConfig(handlers=[logging.FileHandler(os.path.join('logs', 'topnews.log'), 'w', 'utf-8')], level=DEBUG_LEVEL, format='%(asctime)s - %(levelname)s: %(module)s, %(lineno)s, %(funcName)s - %(message)s', datefmt='%d.%m.%y %H:%M:%S')
log = logging.getLogger(__name__)


@dataclass
class Topnews:
    """Topnews: target sites templates"""
    ID: str = ''
    targets: dict = field(default_factory=dict)


    def __post_init__(self):
        self.ID = str(uuid.uuid4())
        self.templates_directory: str = 'targets'
        self.output_directory: str = 'output'


    def run(self):
        log.info('STARTED')
        if not os.path.exists(self.templates_directory):
            log.critical('no templates_directory')
            return None
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)
        for template_file in os.listdir(self.templates_directory):
            if not template_file.endswith('.ini'):
                continue
            target_template_file = os.path.join(self.templates_directory, template_file)
            target = Target(target_template_file)
            log.info(f'{target.name} loaded')
            target_output_file = os.path.join(self.output_directory, target.name)
            if target.scan() is False:
                continue
            log.debug(f'{target=}')
            target_output_content = target.format()
            if target_output_content != '':
                output_file = target.save(target_output_content, target_output_file)
                # webbrowser.open(output_file)
                log.info(f'{target.name} formated and saved')
            else:
                log.error(log.info(f'{target.name} error formating and saving'))
        log.info('FINISHED')


if __name__ == "__main__":
    topnews = Topnews()
    topnews.run()
