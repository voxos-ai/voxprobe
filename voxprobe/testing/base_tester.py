from abc import ABC, abstractmethod

class BaseTester(ABC):
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def run_test(self):
        pass

    @abstractmethod
    def teardown(self):
        pass
