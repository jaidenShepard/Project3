from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Categories, Items

# Database connection
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
user1 = User(name="Edward the Great", email="edwardthegreat@madeup.com",
             picture="http://www.bagulho.net/wp-content/uploads/2011/03/"
                     "Edward-the-Great.jpg")
session.add(user1)
session.commit()

#Items for cars
cars = Categories(name='Cars', user_id=1)
session.add(cars)
session.commit()

m3 = Items(name='BMW M3', description='Pretty cool looking car. Also fast, and'
                                      ' apparently fun to drive. I wouldn\'t '
                                      'know',
           image='http://api.ning.com/files/kV4MbYiv7oR5dmjXk-4z-'
                   'wd6k5xx*EGFRdI0lLHU6D9jPyMP1BcqQWN*zUkTX4HE6pi4xLO361WGmdp4'
                   'RrhO3EI0OA*q5UnE/1082035334.jpeg', category_id=1, user_id=1)
session.add(m3)
session.commit()

fiesta = Items(name='Ford Fiesta ST', description='Looks cool and has an engine'
                                                  ' with more power than an'
                                                  ' engine it size has any'
                                                  ' business having. It\'s'
                                                  ' crazy',
               image='https://photos-1.carwow.co.uk/models/1600x800/'
                       'FiestaST_031.jpg',
               category_id=1, user_id=1)
session.add(fiesta)
session.commit()

gti = Items(name='Volkswagen Golf GTI', description='Zippy and fun to drive '
                                                    'apparently. Maybe avoid '
                                                    'since the whole dieselgate'
                                                    ' thing',
            image='http://www.topgear.com/sites/default/files/styles/'
                    '16x9_1280w/public/cars-car/image/2015/02/buyers_guide_-_'
                    'vw_golf_gti_2014_-_front_quarter.jpg?itok=lwiRtMw0',
            category_id=1, user_id=1)
session.add(gti)
session.commit()


#Items for whatever
consoles = Categories(name='Consoles', user_id=1)
session.add(consoles)
session.commit()

xbox = Items(name='Xbox One', description='Current Microsoft console. Has a '
                                          'very nice controller. '
                                          'Updates frequently. '
                                          'Nearly identical to the PS4',
             image='http://static1.gamespot.com/uploads/original/'
                     '1534/15343359/2823737-6174472236-26119.jpg',
             category_id=2, user_id=1)
session.add(xbox)
session.commit()

ps4 = Items(name='Playstation 4', description='Current Sony console. More '
                                              'powerful than the Xbox One, '
                                              'but otherwise nearly identical',
            image='http://www.geek.com/wp-content/uploads/2016/03/'
                    'PlayStation-4.jpg',
            category_id=2, user_id=1)
session.add(ps4)
session.commit()

wiiu = Items(name='Wii U', description='Great for playing Nintendo games.'
                                       ' Weak hardware otherwise',
             image='http://www.nintendo.com/images/page/wiiu/features/'
                     'hero-1.jpg',
             category_id=2, user_id=1)
session.add(wiiu)
session.commit()


#items for whatever
processors = Categories(name='Processors', user_id=1)
session.add(processors)
session.commit()

amd = Items(name='AMD', description='Advanced Micro Devices is a company that '
                                    'develops processors and graphics cards. '
                                    'Currently they lag behind Intel in '
                                    'performance',
            image='http://i1-news.softpedia-static.com/images/news2/AMD-FX-'
                    '6100-and-FX-4100-Bulldozer-CPUs-Arrive-in-Europe-2.jpg',
            category_id=3, user_id=1)
session.add(amd)
session.commit()

intel = Items(name='Intel', description='Current leader in computer processors.'
                                        ' Unmatched in performance, albeit at a'
                                        ' price premium',
              image='http://cdn.phys.org/newman/gfx/news/hires/2012/'
                      '1-intelintrodu.jpg',
              category_id=3, user_id=1)
session.add(intel)
session.commit()

print('Catalog populated')