import abc


class Observer(object, metaclass=abc.ABCMeta):
    def begin_opportunity_finder(self, depths):
        pass

    def end_opportunity_finder(self):
        pass

    ## abstract
    @abc.abstractmethod
    def opportunity(self, profit, profit_total, volume, buyprice, kask, sellprice, kbid,
                    perc, weighted_buyprice, weighted_sellprice):
        pass
