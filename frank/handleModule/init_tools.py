from frank.handleModule.pod.init_pod import InitTab1
from .init_tab_4 import InitTab4

class InitTools:
    def __init__(self,ui):
        self.tab_1 = InitTab1(ui)
        self.tab_4 = InitTab4(ui)
