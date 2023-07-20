import cherrypy
import requests

class Fetcher(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {
            'hello': 'world'
        }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def dpd(self, parcelno, zip=None):
        r = requests.get(f"https://tracking.dpd.de/rest/plc/de_DE/{parcelno}")

        if (zip == None):
            weblink = f"https://my.dpd.de/redirect.aspx?parcelno={parcelno}&action=2"
        else:
            weblink = f"https://my.dpd.de/redirect.aspx?zip={zip}&parcelno={parcelno}&action=2"
            
        return {
            'parcelno': parcelno,
            'zip': zip,
            'details_link': weblink,
            'orig': r.json()['parcellifecycleResponse']['parcelLifeCycleData']
        }

if __name__ == '__main__':
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(Fetcher())
