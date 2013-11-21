# -*- coding: utf-8 -*-

from zope import schema
from z3c.form import field, form
from collective.z3cform.wizard import wizard
from plone.z3cform.layout import FormWrapper
from Products.statusmessages.interfaces import IStatusMessage
from Products.statusmessages.adapter import _decodeCookieValue
from collective.beaker.interfaces import ISession
from zope.component.hooks import getSite
from zope.component import getMultiAdapter

from five import grok
from plone import api
from .card_step import CardStep
from .family_step import FamilyStep
from .address_step import AddressStep

try:
    from zope.browserpage import viewpagetemplatefile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate import viewpagetemplatefile

# - Intro step
# - Adress
# - Familj + Förening
# - Kort


class IntroStep(wizard.Step):
    prefix = 'intro'
    fields = {}
    label = 'Introduktion'
    index = viewpagetemplatefile.ViewPageTemplateFile('intro.pt')

    def __init__(self, context, request, wizard):
        # Use collective.beaker for session managment
        session = ISession(request, None)
        self.sessionmanager = session

        super(IntroStep, self).__init__(context, request, wizard)

class UtroStep(wizard.Step):
    prefix = 'utro'
    fields = {}
    label = 'Tack!'
    index = viewpagetemplatefile.ViewPageTemplateFile('utro.pt')

    def __init__(self, context, request, wizard):
        # Use collective.beaker for session managment
        session = ISession(request, None)
        self.sessionmanager = session

        super(UtroStep, self).__init__(context, request, wizard)

    def get_url(self):

        url = self.wizard.get_finish_url()
        #import pdb; pdb.set_trace()
        return url  


class Wizard(wizard.Wizard):
    label = u"Kom igång"
    validate_back = False

    def update(self):
        # Use collective.beaker for session managment
        session = ISession(self.request, None)
        self.sessionmanager = session
        
        super(Wizard, self).update()


    @property
    def steps(self):
        steps = [IntroStep, AddressStep, FamilyStep, CardStep, UtroStep]
        return steps

    def applySteps(self, pfg, initial_finish=True):
        """
        Run the apply method for each step in the wizard
        """
        for step in self.activeSteps:
            if hasattr(step, 'apply'):
                step.apply(pfg, initial_finish=initial_finish)
    
    def showClear(self):
        return False

    def get_finish_url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        actions = context_state.actions(category="hejasverige.mymenu")
        if actions:
            url = actions[0]['url']        
            if url:
                return url

        return getSite().absolute_url()

    def finish(self):
        super(Wizard, self).finish()
        url = self.get_finish_url()
        return self.request.response.redirect(url)

class WizardView(FormWrapper):
    form = Wizard
    
    def __init__(self, context, request):
        FormWrapper.__init__(self, context, request)
        request.set('disable_border', 1)
    
    def absolute_url(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)