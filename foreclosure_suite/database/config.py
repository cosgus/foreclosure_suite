from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

creds = config['databases']['postgres']

engine = create_engine(f"postgresql://{creds['user']}:{creds['password']}@localhost/foreclosure", echo = False)

session = scoped_session(
    sessionmaker(
        autocommit = False,
        bind = engine
    )
)


