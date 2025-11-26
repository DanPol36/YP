# models/practic.py
from sqlalchemy import Column, Integer, String, Date
from instance.database import Base

class Person(Base):
    __tablename__ = "practic2"          # имя твоей таблицы в БД
    __table_args__ = {'schema': 'public'}  # если она в схеме public

    id = Column(Integer, primary_key=True, autoincrement=True)  # если нет — добавим
    ФИО = Column(String)
    Пол = Column(String)
    Адрес = Column(String)
    Возраст = Column(Integer)
    Дата_рождения = Column(Date)
    Номер_телефона = Column(String, name="Номер телефона")
    Почта = Column(String)
    Примечания = Column(String)