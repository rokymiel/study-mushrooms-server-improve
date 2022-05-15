import omegaconf
import common.runtime

settings_config = omegaconf.OmegaConf.load(f'{common.runtime.BASE_DIR}/server_configs/settings.yaml')