from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import sessionmaker
from model import Base, BeerType, Beer, User

engine = create_engine('sqlite:///beerbase.db')
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


# Add lager beer type
beerType1 = BeerType(type="Lager")

session.add(beerType1)
session.commit()

# Add lagers
beer1 = Beer(name="5 Points", description="Hoppy beer, with a good head, from London", type_id=beerType1.id)

session.add(beer1)
session.commit()

beer2 = Beer(name="Hell's Lager", description="From Camden brewery, popular lager for good reason", type_id=beerType1.id)

session.add(beer2)
session.commit()

beer3 = Beer(name="Meantime Lager", description="Greenwitch flagship lager, stronger than most but great for a hot day", type_id=beerType1.id)

session.add(beer3)
session.commit()

# Add Pale Ale beer type
beerType2 = BeerType(type="Pale Ale")

session.add(beerType2)
session.commit()

# Add Pale Ales
beer1 = Beer(name="Malt Coast", description="King of Pales from the North Norfolk coast", type_id=beerType2.id)

session.add(beer1)
session.commit()

beer2 = Beer(name="Camden Pale Ale", description="Another solid pale ale from the camden crew", type_id=beerType2.id)

session.add(beer2)
session.commit()

beer3 = Beer(name="London Pale Ale", description="Green and black lable, tastes even better than the chocolate", type_id=beerType2.id)

session.add(beer3)
session.commit()
