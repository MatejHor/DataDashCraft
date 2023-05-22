from sqlalchemy import inspect

class Abstract():

    def __init__(self):
        super().__init_subclass__()

    def to_dict(self):
        return {key: getattr(self, key) for key in self.get_columns()}
    
    @classmethod
    def get_primary_key(cls):
        return inspect(cls).primary_key[0].name
    
    @classmethod
    def get_columns(cls):
        inst = inspect(cls)
        return [c_attr.key for c_attr in inst.mapper.column_attrs]

    @classmethod
    def get_list(cls, session):
        return session.query(cls)
    
    @classmethod
    def get(cls, session, id):
        id_attr = getattr(cls, cls.get_primary_key())
        return session.query(cls).filter(id_attr == id).first()

    @classmethod
    def add(cls, session, item):
        session.add(item)
        session.commit()

    @classmethod
    def update(cls, session, item_db, item_new):
        for key, value in item_new.items():
            field = getattr(item_db, key)
            if field != value:
                setattr(item_db, key, value)
        cls.add(session, item_db)

    @classmethod
    def delete(cls, session, item):
        session.delete(item)
        session.commit()

    @classmethod
    def delete_by_id(cls, session, id):
        id_attr = getattr(cls, cls.get_primary_key())
        session.query(cls).filter(id_attr == id).delete()
        session.commit()
