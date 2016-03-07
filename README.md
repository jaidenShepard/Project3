Catalog Web App Version 1.0 2016/03/07

#Technologies Used
- Python
- Vagrant
- SQLite
- Vagrant/Linux Virtual Environment
- Oauth User authentication with Google and Facebook
- Twitter Bootstrap

#What you'll need
- Vagrant
- Virtual Box
- An internet connection
- Modern Browser

#Setup
1. Install Vagrant and Virtual box
2. Clone the repository to your chosen directory
3. From Terminal/CMD:

    $ cd /vagrant/project3
    $ vagrant up
    $ vagrant ssh
    vagrant=> cd /vagrant/app
    vagrant=> python database_setup.py
    vagrant=> python catalog_populate.py
    vagrant=> python catalog.py

#Using the app
Now that database is populated and the server is up and running, we can access the app by opening a browser and navigating to localhost:5000.
This will bring you to the index page, which gives you a public view of the catalog. By login in through Facebook or Google, the user will be
able to add their own categories and populate them with items of their choice.

#API
Serialized form the categories list can be found at '/categories/JSON'
Serialized item list in a category can be found at '/~category name~/JSON'

#The MIT License (MIT)
Copyright (c) 2016 Jayden Shepard

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
