class Object:
    @property
    def _class(self) -> str:
        return self.__class__.__name__
