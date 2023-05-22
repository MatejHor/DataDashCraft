from sqlalchemy import Column, Integer, String
from helpers.storage import BASE
from helpers.abstract import Abstract

class Project(BASE, Abstract):
    __tablename__ = "project"

    project_id = Column(Integer, primary_key=True)
    project_name = Column(String)
    path = Column(String)
    created_on = Column(String)
    description = Column(String)
