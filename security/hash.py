import hashlib
import pickle
import getpass
import os

saltSeed = getpass.getuser()

def GenHash(query: list):

    assert len(query) in (7,9)

    # get location of hash entry in query; then replace it w/ a constant
    index = 3 if len(query) == 7 else 2
    query[index] = saltSeed

    p = pickle.dumps(query)
    salt = os.urandom(hashlib.blake2b.SALT_SIZE)
    h = hashlib.blake2b(p, salt=salt)

    return(h.digest())