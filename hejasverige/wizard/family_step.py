# -*- coding: utf-8 -*-

from plone import api
from plone.z3cform.crud import crud
from zope import schema
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from z3c.form import field, form
from collective.z3cform.wizard import wizard
from hejasverige.content.person import IPerson
from hejasverige.content.person import IRelation
from hejasverige.content.eventsubscribers import _getFolder
from plone.app.uuid.utils import uuidToObject
import urllib
from collective.beaker.interfaces import ISession

try:
    from zope.browserpage import viewpagetemplatefile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate import viewpagetemplatefile

import logging
logger = logging.getLogger(__name__)


class FamilyStep(wizard.Step):
    # not using crud form yet. But should do.

    label = 'Familj och föreningar'
    template = viewpagetemplatefile.ViewPageTemplateFile('family_step.pt')
    prefix = 'three'
    fields = field.Fields(IPerson)
    description = u'Lägg till familj och föreningar'

    fields = {}

    #update_schema = IOrdered
    addform_factory = crud.NullForm
    #editform_factory = FieldListingForm

    def __init__(self, context, request, wizard):
        # Use collective.beaker for session managment
        session = ISession(request, None)
        self.sessionmanager = session

        super(FamilyStep, self).__init__(context, request, wizard)

    def wizard_url(self):
        #import pdb; pdb.set_trace()
        return urllib.quote(self.wizard.absolute_url)

    def me(self):
        user = api.user.get_current()
        fullname = user.getProperty('fullname')
        if type(fullname).__name__ == 'object':
            fullname = None

        personal_id = user.getProperty('personal_id')
        if type(personal_id).__name__ == 'object':
            personal_id = None

        portrait = user.portal_memberdata.getPersonalPortrait()


        # clubs
        clubs_folder = _getFolder(user.getProperty('id'), 'my-clubs', 'hejasverige.relationfolder')

        catalog = getToolByName(self.context, 'portal_catalog')

        clubs = [dict(club=uuidToObject(relation.getObject().foreign_id), relation=relation.getObject())
                 for relation in
                 catalog({'object_provides': IRelation.__identifier__,
                          'review_state': ('pending', 'approved'),
                          'path': dict(query='/'.join(clubs_folder.getPhysicalPath()),
                                       depth=1),'sort_on': 'sortable_title'})]

        #import pdb; pdb.set_trace()

        #import pdb;pdb.set_trace()
        addrelationurl = '/'.join(clubs_folder.getPhysicalPath()) + '/@@add-relation'

        info = {'name': fullname,
                'personal_id': personal_id,
                'clubs': clubs,
                'portrait': portrait,
                'addrelationurl': addrelationurl,
                }

        return info

    def my_family(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        mship = getToolByName(self.context, 'portal_membership')

        home = mship.getHomeFolder()
        family = catalog({'object_provides': IPerson.__identifier__,
                          'path': dict(query='/'.join(home.getPhysicalPath())), 
                          'sort_on': 'sortable_title'})

        family_objs = [brain.getObject() for brain in family]

        persons = []

        for item in family_objs:
            clubs = [dict(club=uuidToObject(relation.getObject().foreign_id), relation=relation.getObject())
                     for relation in
                     catalog({'object_provides': IRelation.__identifier__,
                              'review_state': ('pending', 'approved'),
                              'path': dict(query='/'.join(item.getPhysicalPath()),
                                           depth=1),'sort_on': 'sortable_title'})]

            clubs = [x for x in clubs if x]
            persons.append({'name': item.first_name + ' ' + item.last_name, 
                            'clubs': clubs, 
                            'person': item})

        return persons

    def add_club_url(self, person):

        #import pdb; pdb.set_trace()

        url = '/'.join(person.get('person').getPhysicalPath()) + '/add-relation'
        #url = '/'.join(club.get('relation').getPhysicalPath()) + '/abort'
        return url


    def remove_club_url(self, club):

        url = '/'.join(club.get('relation').getPhysicalPath()) + '/abort'
        return url

    def add_person_url(self):
        user = api.user.get_current()
        family_folder = _getFolder(user.getProperty('id'), 'my-family', 'Folder')


        #import pdb; pdb.set_trace()
        # string:${context/absolute_url}/++add++hejasverige.person
        url = '/'.join(family_folder.getPhysicalPath()) + '/++add++hejasverige.person'
        return url

    def get_items(self):
        #import pdb;pdb.set_trace()
        return sorted(self._get_fields().items(), key=lambda x: x[1]['order'])

    def add(self, data):
        data['order'] = len(self._get_fields())

        self._get_fields()[id] = data
        self.wizard.sync()
        self.request._added_field = id
        return data

    def remove(self, (id, item)):
        del self._get_fields()[id]
        self.wizard.sync()

    def _get_fields(self):
        #import pdb; pdb.set_trace()
        data = self.getContent()
        if 'fields' in data:
            return data['fields']
        
        # initialize fields
        fields = {
            'field1': {
                'field_type': 'text',
                'title': u'Faltets titel',
                'description': u'Faltets beskrivning',
                'default': u'Faltets defaultvärde',
                'required': True,
                'order': 0,
                },
            'field2': {
                'field_type': 'text',
                'title': u'Faltet2s titel',
                'description': u'Faltet2s beskrivning',
                'default': u'Faltet2s defaultvärde',
                'required': True,
                'order': 0,
                },
            }
        return self.getContent().setdefault('fields', fields)

'''
from plone.z3cform.crud import crud
from plone.z3cform.tests import setup_defaults
from plone.z3cform.layout import wrap_form

setup_defaults()

#from zope import interface, schema
#class IPerson(interface.Interface) :
#    name = schema.TextLine()
#    age = schema.Int()

#class Person(object):
#    interface.implements(IPerson)
#    def __init__(self, name=None, age=None):
#        self.name, self.age = name, age
#    def __repr__(self):
#        return "<Person with name=%r, age=%r>" % (self.name, self.age)

# names - keys in storage
#storage = {'Peter': Person(u'Peter', 16),
#           'Martha': Person(u'Martha', 32)}

# form def
class MyForm(crud.CrudForm):
    update_schema = IPerson
    view_schema = IPerson
    #addform_factory = crud.NullForm    
    template = viewpagetemplatefile.ViewPageTemplateFile('testview_form.pt')

    def _get_persons(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        mship = getToolByName(self.context, 'portal_membership')

        home = mship.getHomeFolder()
        family = catalog({'object_provides': IPerson.__identifier__,
                          'path': dict(query='/'.join(home.getPhysicalPath())),
                          'sort_on': 'sortable_title'})

        family_objs = [brain.getObject() for brain in family]

        persons = {}

        for item in family_objs:
            clubs = [dict(club=uuidToObject(relation.getObject().foreign_id),
                          relation=relation.getObject())
                     for relation in
                     catalog({'object_provides': IRelation.__identifier__,
                              'review_state': ('pending', 'approved'),
                              'path': dict(query='/'.join(item.getPhysicalPath()),
                                           depth=1),'sort_on': 'sortable_title'})]

            clubs = [x for x in clubs if x]
            persons[item.id] = dict(first_name=item.first_name, 
                                             last_name=item.last_name, 
                                             personal_id=item.personal_id, 
                                             avatar=item.avatar)

        return persons

    def get_items(self):
        return sorted(self._get_persons().items(), key=lambda x: x[0])
        #return sorted(storage.items(), key=lambda x: x[1].name)

    def add(self, data):
        user = api.user.get_current()
        container = _getFolder(user.getProperty('id'), 'my-family', 'Folder')

        import uuid
        import transaction
        from zope.container.interfaces import INameChooser

        #import pdb; pdb.set_trace()
        data['id'] = str(uuid.uuid4())
        id = container.invokeFactory('hejasverige.person', id=data.get('id'))
        transaction.savepoint(optimistic=True)
        new_obj = container._getOb(id)
        title = "%s %s" % (data.get('first_name'), data.get('last_name'))
        oid = INameChooser(container).chooseName(title, new_obj)
        new_obj.first_name = data.get('first_name')
        new_obj.last_name = data.get('last_name')
        new_obj.personal_id = data.get('personal_id')
        new_obj.avatar = data.get('avatar')
        new_obj.id = oid
        new_obj.reindexObject()

        return oid

        #person = Person(**data)
        #storage[str(person.name)] = person
        #return person

    def remove(self, (id, item)):
        user = api.user.get_current()
        container = _getFolder(user.getProperty('id'), 'my-family', 'Folder')

        #import pdb; pdb.set_trace()
        container.manage_delObjects([id,])
        #del storage[id]
        
    


#MyView = wrap_form(MyForm)
from plone.z3cform.layout import FormWrapper

class TestView(FormWrapper):
    form = MyForm
    
    def __init__(self, context, request):
        FormWrapper.__init__(self, context, request)
        request.set('disable_border', 1)
    
    def absolute_url(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)
'''