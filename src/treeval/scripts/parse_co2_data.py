import io

class ParseCo2Data:

    def __init__(self, contents: list) -> None:
        self.headers        = contents

        self.collection     = self.__iter__()


    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]
        txt.write(")")
        return txt.getvalue()


    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]
        txt.write(")")
        return txt.getvalue()