from sqlalchemy import Column, Integer, String
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from api.web_app import get_db

# from sqlalchemy.orm import declarative_base
# Base = declarative_base()

class SmartMeter(get_db().Model):
    # __tablename__ = "smart_meter"
    id = Column(Integer, primary_key=True)
    em_SniffingRate = Column(String)
    em_Type = Column(String)
    em_Status = Column(String)
    em_RdTime = Column(String)
    em_Queries = Column(String)
    em_TotErr = Column(String)
    em_ErrRate = Column(String)
    em_LastErr = Column(String)
    em_Uab = Column(String)
    em_Ubc = Column(String)
    em_Uca = Column(String)
    em_Ua = Column(String)
    em_Ub = Column(String)
    em_Uc = Column(String)
    em_Ia = Column(String)
    em_Ib = Column(String)
    em_Ic = Column(String)
    em_Pt = Column(String)
    em_Pa = Column(String)
    em_Pb = Column(String)
    em_Pc = Column(String)
    em_Qt = Column(String)
    em_Qa = Column(String)
    em_Qb = Column(String)
    em_Qc = Column(String)
    em_PFt = Column(String)
    em_PFa = Column(String)
    em_PFb = Column(String)
    em_PFc = Column(String)
    em_Freq = Column(String)

    em_ImpEp = Column(String)
    em_ExpEp = Column(String)
    em_Q1Eq = Column(String)
    em_Q2Eq = Column(String)
    em_Q3Eq = Column(String)
    em_Q4Eq = Column(String)
    
# Create data abstraction layer


class SmartMeterSchema(Schema):
    class Meta:
        type_ = 'smartmeter'
        self_view = 'smartmeter_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'smartmeter_many'

    id = fields.Integer()
    em_SniffingRate = fields.Str(required=True)
    em_Type = fields.Str(required=True)
    em_Status = fields.Str(required=True)
    em_RdTime = fields.Str(required=False)
    em_Queries = fields.Str(required=False)
    em_TotErr = fields.Str(required=False)
    em_ErrRate = fields.Str(required=False)
    em_LastErr = fields.Str(required=False)
    em_Uab = fields.Str(required=False)
    em_Ubc = fields.Str(required=False)
    em_Uca = fields.Str(required=False)
    em_Ua = fields.Str(required=False)
    em_Ub = fields.Str(required=False)
    em_Uc = fields.Str(required=False)
    em_Ia = fields.Str(required=False)
    em_Ib = fields.Str(required=False)
    em_Ic = fields.Str(required=False)
    em_Pt = fields.Str(required=False)
    em_Pa = fields.Str(required=False)
    em_Pb = fields.Str(required=False)
    em_Pc = fields.Str(required=False)
    em_Qt = fields.Str(required=False)
    em_Qa = fields.Str(required=False)
    em_Qb = fields.Str(required=False)
    em_Qc = fields.Str(required=False)
    em_PFt = fields.Str(required=False)
    em_PFa = fields.Str(required=False)
    em_PFb = fields.Str(required=False)
    em_PFc = fields.Str(required=False)
    em_Freq = fields.Str(required=False)

    em_ImpEp = fields.Str(required=False)
    em_ExpEp = fields.Str(required=False)
    em_Q1Eq = fields.Str(required=False)
    em_Q2Eq = fields.Str(required=False)
    em_Q3Eq = fields.Str(required=False)
    em_Q4Eq = fields.Str(required=False)
# Create resource managers and endpoints
