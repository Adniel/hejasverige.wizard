from five import grok
from Products.PlonePAS.interfaces.events import IUserInitialLoginInEvent
from zope.component.hooks import getSite


#@grok.subscribe(IUserInitialLoginInEvent)
def logged_in_handler(event):
    """
    Listen to the event and perform the action accordingly.
    """
    #user = event.object
    site = getSite()

    # We need to access the HTTP requesrt object via
    # acquisition as it is not exposed by the event
    request = getattr(site, "REQUEST", None)
    if not request:
        # HTTP request is not present e.g.
        # when doing unit testing / calling scripts from command line
        return False

    #import pdb; pdb.set_trace()
    request.response.redirect(site.absolute_url() + "/wizard")
