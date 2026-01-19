from abc import ABC, abstractmethod

class BaseCore(ABC):

    @abstractmethod
    def ejecutar(self, *args):
        pass
