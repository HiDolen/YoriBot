from utils.plugin_manager.plugin_info import PluginInfo
from utils.plugin_manager.plugin_status import PluginStatus

from configs.path_config import DATA_PATH


class Plugin_Manager:
    def __init__(self) -> None:
        path = DATA_PATH / "plugin_manager"
        self.plugin_info: PluginInfo = PluginInfo(path / "plugin_info.json")
        self.plugin_status: PluginStatus = PluginStatus(path / "plugin_status.json")
