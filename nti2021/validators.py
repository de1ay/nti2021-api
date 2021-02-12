from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
import re


class MaximumLengthValidator(object):
    def validate(self, password, user=None):
        if len(password) > 20:
            raise ValidationError(
                _("Пароль слишком длинный (больше 20 символов)"),
                code='password_too_long',
                params={'min_length': 20},
            )

    def get_help_text(self):
        return _(
            "Пароль слишком длинный (больше %(max_length)d символов)."
            % {'max_length': 20}
        )


class OneHighCaseValidator(object):
    def validate(self, password, user=None):
        if str.islower(password):
            raise ValidationError(
                _("Пароль не содержит заглавных букв."),
                code='password_lower',
            )

    def get_help_text(self):
        return _(
            "Пароль не содержит заглавных букв."
        )


class OneZnakValidator(object):
    def validate(self, password, user=None):
        regex = r'[._^%$#!~@,-]'
        if not re.findall(regex, password):
            raise ValidationError(
                _("Проверка наличия в пароле хотя бы одного знака препинания при регистрации нового пользователя или смене им пароля"),
                code='password_znak',
            )

    def get_help_text(self):
        return _(
            "Проверка наличия в пароле хотя бы одного знака препинания при регистрации нового пользователя или смене им пароля"
        )


class OneNumberValidator(object):
    def validate(self, password, user=None):
        regex = r'[0-9]'
        if not re.findall(regex, password):
            raise ValidationError(
                _("Проверка наличия в пароле хотя бы одной цифры при регистрации нового пользователя или смене им пароля"),
                code='password_znak',
            )

    def get_help_text(self):
        return _(
            "Проверка наличия в пароле хотя бы одной цифры при регистрации нового пользователя или смене им пароля"
        )

