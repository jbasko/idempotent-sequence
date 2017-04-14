from idemseq.base import FunctionWrapper, OptionsWithName


class ProviderOptions(OptionsWithName):
    pass


class Provider(FunctionWrapper):
    options_class = ProviderOptions
