# -*- coding: utf-8 -*-

from plone import api
from plone.z3cform.fieldsets import group

from zope import schema
from plone.namedfile.field import NamedImage

from zope.component import getUtility
from zope.component.hooks import getSite
from z3c.form import field, form

from collective.z3cform.wizard import wizard
try:
    from zope.browserpage import viewpagetemplatefile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate import viewpagetemplatefile

import logging
logger = logging.getLogger(__name__)

class PersonalInfoGroup(group.Group):

    # fix so that default user image is not wrapped in acquisition before adding that to the wizard. It can not be pickled. (http://pastie.org/8474225)
    fields = field.Fields(
        #NamedImage(__name__='portrait', title=u"Porträtt", required=False),
        schema.TextLine(__name__='fullname', title=u"Namn", required=False),
        schema.TextLine(__name__='personal_id', title=u"Personnummer", required=True),
    )
    label = u"Personuppgifter"
    prefix = 'personalinfo'


class AddressGroup(group.Group):
    fields = field.Fields(        
        schema.TextLine(__name__='address1', title=u"Adress 1", required=False),
        schema.TextLine(__name__='address2', title=u"Adress 2", required=False),
        schema.TextLine(__name__='postal_code', title=u"Postadress", required=False),
        schema.TextLine(__name__='city', title=u"Stad", required=False),
    )
    label = u"Adressuppgifter"
    prefix = 'address'


class AddressStep(wizard.GroupStep):
    prefix = 'Address'
    label = 'Person- och adressuppgifter'
    description = 'Kontrollera dina person- och addressuppgifter'

    template = viewpagetemplatefile.ViewPageTemplateFile('address_step.pt')
    fields = field.Fields()
    groups = [PersonalInfoGroup, AddressGroup]

    #def updateWidgets(self):
        
        #super(AddressStep, self).updateWidgets()
        # does not work as GroupStep inherits from group.GroupForm and Step or somethin like that
        #wizard.GroupStep.updateWidgets(self)

        #import pdb; pdb.set_trace()
        #self.widgets['address2'].extra += 'plaholder="blah!"'


    def load(self, context):
        member = api.user.get_current()
        data = self.getContent()

        # Personal info group
        #import pdb; pdb.set_trace()
        #if not data.get('portrait', None):
        #    portrait = member.getPersonalPortrait()
        #    data['portrait'] = portrait

        if not data.get('fullname', None):
            fullname = member.getProperty('fullname')
            if type(fullname).__name__ == 'object':
                fullname = None
            data['fullname'] = fullname

        if not data.get('personal_id', None):
            personal_id = member.getProperty('personal_id')
            if type(personal_id).__name__ == 'object':
                personal_id = None
            data['personal_id'] = personal_id

        # Address group
        if not data.get('address1', None):
            address1 = member.getProperty('address1')
            if type(address1).__name__ == 'object':
                address1 = None
            data['address1'] = address1

        if not data.get('address2', None):
            address2 = member.getProperty('address2')
            if type(address2).__name__ == 'object':
                address2 = None
            data['address2'] = address2

        if not data.get('postal_code', None):
            postal_code = member.getProperty('postal_code')
            if type(postal_code).__name__ == 'object':
                postal_code = None
            data['postal_code'] = postal_code

        if not data.get('city', None):
            city = member.getProperty('city')
            if type(city).__name__ == 'object':
                city = None
            data['city'] = city


    def apply(self, context, initial_finish=False):
        data = self.getContent()

    def applyChanges(self, data):
        member = api.user.get_current()
        member.setMemberProperties(mapping={'fullname': data['fullname'], 'personal_id': data['personal_id'],'address1': data['address1'], "address2": data['address2'], "city": data['city'], "postal_code": data['postal_code']})
        #member.setPersonalPortrait(data['portrait'])


