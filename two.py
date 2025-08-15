from fastapi import FastAPI,HTTPException,Path,Query
from pydantic import BaseModel,Field,computed_field
from fastapi.responses import JSONResponse
from typing import Annotated,Literal,Optional
import json
app=FastAPI()

class Student(BaseModel):
    id:Annotated[str,Field(...,description="Enter your id")]
    name:Annotated[str,Field(...,description="Enter your name",max_length=50)]                                          # "name": "Alice Johnson",
    age: Annotated[int,Field(...,description="Enter your age",gt=0,lt=20)]
    city:Annotated[str,Field(...,description="Enter your city")]
    gender:Annotated[Literal["Male","Female"],Field(...,description="Enter your gender")]
    height:Annotated[float,Field(...,description="Enter your height",gt=0)]
    weight:Annotated[float,Field(...,description="Enter your wEight",gt=0)]
    
    @computed_field
    @property
    def bmi(self)->float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
               return "Underweight"
        elif self.bmi<25:
            return "Normal"
        elif self.bmi<30:
            return "Normal"
        else:
            return "Obese"



#First message
@app.get("/")
def view():
    return {"message":"This is about Student Data"}

#About this page
@app.get("/about")
def about():
    return {"message":"The student dataset contains basic demographic and physical attributes of five students.This data can be used for sorting, searching, or updating student health records in the FastAPI application"}

#load_data
with open("students.json","r") as f:
    data=json.load(f)
    
#visual load_data  
@app.get("/load_data")
def load_data():
    return data

#Find individual patient data
@app.get("/students/{student_id}")
def student_(student_id:str=Path(...,description="Enter student ID",example="S001")):
    data=load_data()
    if student_id not in data:
        raise HTTPException(status_code=404,detail='Entered Student Id Not present')
    return data[student_id]

#Sort the data 
@app.get("/sort")
def sort_(sort_by:str=Query(...,description="Choose among height,weight,bmi"),
          order_by:str=Query(...,description="Choose between asc or desc")):
    data=load_data()
    valid_details=["height","weight","bmi"]
    if sort_by not in valid_details:
        raise HTTPException(status_code=404,detail="Please add valid detail")
    order=True if order_by=="desc" else False
    sort__=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=order)
    return sort__

def save_data(data):
    with open("students.json","w") as f:
        json.dump(data,f)

#create a new student -Add new data to the database
@app.post("/create")
def add_student(student:Student):
    data=load_data()
    if student.id in data:
        raise HTTPException(status_code=404,detail="Student data already present")
    
    data[student.id]=student.model_dump(exclude=["id"])
    
    save_data(data)
    
    return JSONResponse(status_code=201,content={"message":"New Student data created"})

class student_update(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    gender:Annotated[Literal["Male","Female","Others"],Field(default=None)]
    height:Annotated[Optional[float],Field(default=None,gt=0)]
    weight:Annotated[Optional[float],Field(default=None,gt=0)]
    

#Update 
@app.put("/edit/{student_id}")
def update(student_id:str,student_update:student_update):
    data=load_data()
    if student_id not in data:
        raise HTTPException(status_code=404,detail="The Entered student id does not present")
    exist_student_info=data[student_id]
    
    update_student_info=student_update.model_dump(exclude_unset=True)
    
    for key,values in update_student_info.items():
        exist_student_info[key]=values
        
    exist_student_info["id"]=student_id
    pydantic_obj=Student(**exist_student_info)
    exist_student_info=pydantic_obj.model_dump(exclude=["id"])
    
    data[student_id]=exist_student_info
    
    save_data(data)
    
    return JSONResponse(status_code=201,content={"message":"Student data updated"})

#Delete 
@app.delete("/student/delete/{student_id}")
def delete(student_id:str):
    data=load_data()
    if student_id not in data:
        raise HTTPException(status_code=404,detail="Invalid Student Id")
    
    del data[student_id]
        
    save_data(data)
    
    return JSONResponse(status_code=201,content={"message":"Your entered student id is deleted"})