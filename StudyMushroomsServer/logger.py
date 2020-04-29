import logging

base_logger = logging.getLogger('gid_srv')
base_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s  [%(name)s] [%(levelname)s]: %(message)s')
handler = logging.FileHandler('server.log', mode='w')
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
base_logger.addHandler(handler)
base_logger.info("Launching logging")