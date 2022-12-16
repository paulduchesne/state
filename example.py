import state
import pathlib

# identify individual who is making statements.
state.me('paul duchesne', '1986-04-14')

# identify another individual.
state.person('philip kindred dick', '1928-12-16')

# identify multiple people.
state.people([
    {"name": "Karl Ove Knausgård", "birth": "1968-12-06"}, 
    {"name": "Linda Boström Knausgård", "birth": "1972-10-15"}])

# identify file which is owned by individual.
state.file(pathlib.Path.home() / '02.flac')

# decrypt all statements in personal graph.
state.decrypt_all()
