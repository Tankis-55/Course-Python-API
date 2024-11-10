import os
from dotenv import load_dotenv  # Import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, select
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
 

#Load enviroment from variables from .env file
load_dotenv()

#Database URI from render DONT FORGER postgresql+asyncpg://
DATABASE_URL = f'postgresql+asyncpg://course_python_db_f9pf_user:szSDy5PGP8h1vIefYlzol7CU1ottnpJ8@dpg-csoafaogph6c73boprk0-a.oregon-postgres.render.com/course_python_db_f9pf'



#Intitialization SQLAlchemy
engine = create_async_engine(DATABASE_URL, ech=True)
SessinLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine, class_=AsyncSession)
Base = declarative_base()


app = FastAPI()


#Allow origins (for development purpose only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)   

class ItemDB(Base):
    _tablename_ = 'items'
    id= Column(Integer, primery_key=True, index=True)
    description = Column(String, index=True)
    price = Column(Float)
    avaliable = Column(Boolean, defualt=True)

    #Create the tables

@app.on_event('startup') 
async def on_startup():
    async with engine.beggin() as conn:
        await conn.run_async(Base.metadata.create_all)



#Pydantic models for APIninput/output
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    avaliable: bool = True

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    avaliable: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)

#Dependency to get the async session for each request
async def get_db():
    async with SessinLocal()  as session:
        yield session

@app.get('/')
async def root():
    return {'message': 'Service is running'}

#GET : Retrieve all items
@app.get('/items', response_model=List[Item])
async def get_items(db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemDB))
    items = result.scalar().all()
    return items


#GET : Retrieve item by ID
@app.get('/items/{item_id}', response_mode=Item)
async def get_item(item_id:int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemDB).filter(ItemDB.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, delail='Item not Found')
    return item
