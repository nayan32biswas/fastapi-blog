class staticproperty(staticmethod):
    def __get__(self, *_):
        return self.__func__()
