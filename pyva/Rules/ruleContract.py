import abc


class RuleContract:

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def passes(self, attribute, value):
        raise NotImplementedError
