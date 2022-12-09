import state

# identify individual who is making statements.
state.me('paul duchesne', '1986-04-14')

# identify another individual.
state.person('philip kindred dick', '1928-12-16')

# identify file which is owned by individual.
# state.file(file_path)

# decrypt all statements in personal graph.
state.decrypt_all()
