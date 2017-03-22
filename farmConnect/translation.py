from modeltranslation.translator import translator, TranslationOptions
from farmConnect.models import Produce,ProduceCategory

class ProduceTranslationOptions(TranslationOptions):
    fields = ('name',)
class ProduceCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Produce, ProduceTranslationOptions)
translator.register(ProduceCategory, ProduceCategoryTranslationOptions)