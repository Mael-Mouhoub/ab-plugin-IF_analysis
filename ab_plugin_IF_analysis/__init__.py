import activity_browser as ab

#from .layouts.tabs import LeftTab, RightTab
from .layouts.tabs import RightTab


class Plugin(ab.Plugin):

    def __init__(self):
        infos = {
            'name': "IF_analysis",
        }
        ab.Plugin.__init__(self, infos)

    def load(self):
        self.rightTab = RightTab(self)
        #self.leftTab = LeftTab(self)
        #self.tabs = [self.rightTab, self.leftTab]
        self.tabs = [self.rightTab]

    def close(self):
        return

    def remove(self):
        return