#!/usr/bin/env python
from flaskexample import app
app.run(host='0.0.0.0',debug=True)

# The script simply imports the app variable from our flaskexample 
# package and invokes its run method to start the server. Remember 
# that the app variable holds the Flask instance, we created it above.

# To start the app
# chmod a+x run.py