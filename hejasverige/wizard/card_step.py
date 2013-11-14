# -*- coding: utf-8 -*-

from plone import api
from zope import schema
from zope.component import getUtility
from zope.component.hooks import getSite
from z3c.form import field, form, button
from collective.z3cform.wizard import wizard
from hejasverige.kollkoll.interfaces import IKollkollCard
from hejasverige.kollkoll.interfaces import IKollkoll
from collective.beaker.interfaces import ISession
from hejasverige.kollkoll.config import SessionKeys

import urllib

from . import _

try:
    from zope.browserpage import viewpagetemplatefile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate import viewpagetemplatefile

import logging
logger = logging.getLogger(__name__)

try:
    from hejasverige.kollkoll.kollkoll import Kollkoll
except ImportError:
    logger.exception("Kollkoll is not installed", *args)

from .config import KOLLKOLLPATH

def get_pid():
    user = api.user.get_current()
    pid = user.getProperty('personal_id')
    if type(pid).__name__ == 'object':
        pid = None
    return pid

class CardAddForm(form.Form):
    #ignoreContext = True

    fields = field.Fields(IKollkollCard)

    #if not schema.providedBy(self.context):
    #    alsoProvides(self.context, IKollkollCard)

    @button.buttonAndHandler(_(u'Lägg till'))
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = form.AddForm.formErrorsMessage
            return
        
        wizard = self.context.form_instance
        wizard.update()
        try:
            item = wizard.currentStep.add(data)
            self._finished = True
        except schema.ValidationError, e:
            self.status = e
        else:
            notify(ObjectCreatedEvent(item))
            self.status = _(u'Kort lades till')



class CardStep(wizard.Step):
    label = 'Registrera betalkort'
    description = ''

    template = viewpagetemplatefile.ViewPageTemplateFile('card_step.pt')
    prefix = 'two'
    fields = field.Fields(
       schema.TextLine(__name__='name', title=u"Name", required=True),
       schema.TextLine(__name__='bank', title=u'Favorite Bank', required=True),
    )

    def __init__(self, context, request, wizard):
        # Use collective.beaker for session managment
        session = ISession(request, None)
        session.auto = 'on'
        self.sessionmanager = session

        super(CardStep, self).__init__(context, request, wizard)


    def connected_banks(self):
        kollkoll = Kollkoll()

        result =  kollkoll.listCards(get_pid())
        session = ISession(self.request, None)
        session[SessionKeys.available_cards] = result
        session.save()

        #import pdb; pdb.set_trace()
        return result

    def get_kollkoll_url(self):
        portal = getSite()
        url = '/'.join(portal.getPhysicalPath()) + '/' + KOLLKOLLPATH
        return url

    def _get_kollkoll_cards(self):
        kollkoll = Kollkoll()
        #import pdb; pdb.set_trace()
        result = [(x.get('id'), x.get('name')) for x in kollkoll.listCards(get_pid(), list_all=True)]
        return result
    
    def get_items(self):
        items = []
        #import pdb; pdb.set_trace()
        for id, item in self._get_kollkoll_cards():
            items.append({
                'id': id,
                'label': item,
                })
        return sorted(items, key=lambda x: x['label'])

    def wizard_url(self):
        #import pdb; pdb.set_trace()
        return urllib.quote(self.wizard.absolute_url)


from plone.z3cform.layout import FormWrapper

class CardAddView(FormWrapper):
    form = CardAddForm
    
    def __init__(self, context, request):
        FormWrapper.__init__(self, context, request)
        request.set('disable_border', 1)
    
    def absolute_url(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)