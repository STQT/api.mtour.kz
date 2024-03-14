from modeltranslation.translator import translator, TranslationOptions

from .models import (PublicOffer, OrderRules,
                     PersonalInfoProtection, Refunds,
                     SiteRules)


class PublicOfferTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


translator.register(PublicOffer, PublicOfferTranslationOptions)


class SiteRulesTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


translator.register(SiteRules, SiteRulesTranslationOptions)


class RefundsTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


translator.register(Refunds, RefundsTranslationOptions)


class PersonalInfoProtectionTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


translator.register(PersonalInfoProtection, PersonalInfoProtectionTranslationOptions)


class OrderRulesTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


translator.register(OrderRules, OrderRulesTranslationOptions)
