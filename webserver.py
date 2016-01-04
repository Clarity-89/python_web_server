from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# Import CRUD operations and database classes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

# Create session and connect to the DB
engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "Hello!</body></html>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print(self.path)
                return
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Get all the restaurants from the DB
                restaurants = session.query(Restaurant).all()
                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>Add a new restaurant</a><br>"
                output += "<ul>"
                for restaurant in restaurants:
                    output += "<li>"
                    output += "%s" % restaurant.name
                    output += "</li>"
                    output += "<a href='restaurants/%s/edit'>Edit</a><br>" % restaurant.id
                    output += "<a href='restaurants/%s/delete'>Delete</a>" % restaurant.id
                output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>'''
                output += '''<input name="name" type="text" placeholder='Name of new restaurant'>'''
                output += '''<input type="submit" value="Create"></form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print(output)
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                pathId = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(id=pathId).one()
                output = ""
                output += "<html><body>"
                output += "<h2> %s </h2>" % restaurant.name
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>''' % pathId
                output += '''<input name="rename" type="text" placeholder='%s'>''' % restaurant.name
                output += '''<input type="submit" value="Rename"></form>'''
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                pathId = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(id=pathId).one()
                output = ""
                output += "<html><body>"
                output += "<h2> Are you sure you want to delete %s?</h2>" % restaurant.name
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>''' % pathId
                output += '''<input type="submit" value="Delete"></form>'''
                output += "</body></html>"
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, 'File Not Found %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    namecontent = fields.get('name')[0]

                restaurant = Restaurant(name=namecontent)
                session.add(restaurant)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    new_name = fields.get('rename')[0]

                pathId = self.path.split('/')[2]
                session.query(Restaurant).filter_by(id=pathId).one()
                restaurant.name = new_name
                session.add(restaurant)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/delete"):

                pathId = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(id=pathId).one()
                session.delete(restaurant)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print("Stopping web server...")
        server.socket.close()


if __name__ == '__main__':
    main()