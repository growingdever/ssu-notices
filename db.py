from sqlalchemy import create_engine, Column, Integer, BIGINT, TIMESTAMP, String
engine = create_engine('sqlite:///database.db')

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import text


class UniversityNoticeModel(Base):
    __tablename__ = 'university_notices'
    
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    type = Column(
        String,
        nullable=False
    )
    title = Column(
        String,
        nullable=False
    )

    @hybrid_property
    def document_link(self):
        document_link_format = 'http://www.ssu.ac.kr/web/kor/plaza_d_01' \
                               '?p_p_id=EXT_MIRRORBBS' \
                               '&_EXT_MIRRORBBS_struts_action=%2Fext%2Fmirrorbbs%2Fview_message' \
                               '&_EXT_MIRRORBBS_messageId={}'
        return document_link_format.format(self.id)

Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
db_session_maker = sessionmaker(bind=engine)
