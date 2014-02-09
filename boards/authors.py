from django.utils.translation import ugettext_lazy as _

ROLE_AUTHOR = _('author')
ROLE_DEVELOPER = _('developer')
ROLE_JS_DEV = _('javascript developer')
ROLE_DESIGNER = _('designer')

authors = {
    'prosperodesu: {
        'name': 'Evgeniy Cirnov',
        'contacts': ['htttp://vk.com/obivan784'],
        'roles': [ROLE_AUTHOR, ROLE_DEVELOPER],
    }
    #'anon': {
        #'name': 'Anob',
        #'contacts': ['anon@anon.com'],
        #'roles': [ROLE_AUTHOR, ROLE_DEVELOPER],
    #},
}
