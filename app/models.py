from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base

class ClusterDefinition(Base):
    __tablename__ = "cluster_definitions"

    cluster_label = Column(Integer, primary_key=True, index=True)
    cluster_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String(10), nullable=False)
    age = Column(Integer, nullable=False)
    annual_income = Column(Integer, nullable=False)
    spending_score = Column(Integer, nullable=False)
    cluster_label = Column(Integer, ForeignKey("cluster_definitions.cluster_label"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())