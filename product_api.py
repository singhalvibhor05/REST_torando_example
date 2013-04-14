import markdown
import os.path
import re
import tornado.auth
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata

from tornado.options import define, options

define("port", default=8080, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1", help="api database host")
define("mysql_database", default="product_api", help="product_api database name")
define("mysql_user", default="root", help="product_api database user")
define("mysql_password", default="123", help="product_api database password")


class Application(tornado.web.Application):
    def __init__(self):
        project_dir = os.getcwd()
        handlers = [
            (r"/", ProductsHandler),
            (r"/product/([0-9]+)", ProductsHandler),
            (r"/all_product/", ProductsHandler),
        ]
        settings = dict(
            #autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class ProductsHandler(BaseHandler):
    def get(self, id=None):
        #book_id = self.get_argument('book_id', None)
        if id:
            entries = self.db.query("SELECT * FROM product WHERE ID="+id)
        else:
            entries = self.db.query("SELECT * FROM product")
        result = {}
        result["product"]=[]
        for entrie in entries:
            result["product"].append({"id":entrie.id, "name":entrie.name, "price":entrie.price})
        self.write(result)

    def post(self):
        try:
            print "Adding new book"
            name = self.get_argument("name")
            title = self.get_argument("price")
            if not name or not price:
                return self.write({"success":False})
            if not len(name) or not len(price):
                return self.write({"success":False})
                
            print "[ NEW PRODUCT ] name ",name," price ",price
            self.db.execute(
                "INSERT INTO product (name,price) VALUES (%s,%s,%s)",name, price)
            self.write({"success":True})
        except:
            self.write({"success":False})


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
