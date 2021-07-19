# =======================================================================
# Author: Jeff
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# If not, see <http://www.gnu.org/licenses/>.
# =======================================================================

import sqlite3
from loguru import logger

class MyDB:

    def __init__(self):
        self.conn = sqlite3.connect("db/line.db")
        self.c = self.conn.cursor()

    def init_db(self):
        try:
            self.c.execute('''CREATE TABLE IF NOT EXISTS Line
                    (token text, uid text)''')
        except Exception as _:
            logger.warning(f"Error: {_}")

    def insert_db(self, Token, uid):
        try:
            self.c.execute('DELETE  FROM Line')
            self.c.execute("INSERT INTO Line VALUES (?,?)", (Token, uid))
        except:
            self.init_db()
        finally:
            self.c.execute('DELETE  FROM Line')
            self.c.execute("INSERT INTO Line VALUES (?,?)", (Token, uid))
            self.conn.commit()

    def select_db(self):
        try:
            self.c.execute("SELECT * FROM Line")
        except:
            self.init_db()
        finally:
            self.c.execute("SELECT * FROM Line")
            query = self.c.fetchone()
            if query:
                Token = query[0]
                Uid = query[1]
                return True, Token, Uid
            else:
                return False, None, None

    def close_db(self):
        self.conn.close()