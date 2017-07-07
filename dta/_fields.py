class Field(object):
    def __init__(self, length: int, required: bool = True, value=None):
        print('Field init')
        self.length = length
        self.required = required
        self.__set__(self, value)

    def __set__(self, instance, value):
        print(f'field set: {instance} {value} ')
        self.value = value

    def __get__(self, instance, owner) -> str:
        print(f'{self} {instance} {owner}')
        print(f'get: {instance} {owner} -> {self.value}')
        return self.value

    # def __str__(self):
    #     return str(self.value)

    def validate(self) -> [str]:
        if self.value is not None and len(self.value) > self.length:
            return [f'[{self.__class__.__name__}] TOO LONG: {self.value} can be at most {self.length} characters']
        return []

