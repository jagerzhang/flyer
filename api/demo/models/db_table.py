# # -*- coding: utf-8 -*-
""" Flyer 框架中对 MySQL 表的试用示例
"""
# from sqlalchemy import Column, String, Integer, Text, Boolean
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class TableDemo(Base):
#     """ MySQL 数据库定义表结构
#     """
#     __tablename__ = "t_demo"
#     id = Column(Integer, primary_key=True, index=True)
#     demo_key = Column(String(64),
#                       nullable=False,
#                       unique=True,
#                       index=True,
#                       comment="demo唯一Key")
#     demo_name = Column(String(64),
#                        nullable=False,
#                        default="Flyer",
#                        comment="Demo名称")
#     comment = Column(Text, nullable=False, comment="备注")

#     def to_dict(self):
#         return {c.name: getattr(self, c.name)
#                 for c in self.__table__.columns}  # NOQA
