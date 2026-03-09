from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import func

import models
import csv
import io

from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def get_db():
    return SessionLocal()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, search: str = ""):

    db = get_db()

    query = db.query(models.Student)

    if search:
        query = query.filter(models.Student.name.contains(search))

    students = query.all()

    total_students = db.query(models.Student).count()

    avg_gpa = db.query(func.avg(models.Student.gpa)).scalar()

    students_by_major = db.query(
        models.Student.major,
        func.count(models.Student.student_id)
    ).group_by(models.Student.major).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "students": students,
            "total_students": total_students,
            "avg_gpa": avg_gpa,
            "students_by_major": students_by_major
        }
    )


@app.get("/add", response_class=HTMLResponse)
def add_form(request: Request):

    db = get_db()

    classes = db.query(models.Class).all()

    return templates.TemplateResponse(
        "form.html",
        {"request": request, "classes": classes, "student": None}
    )


@app.post("/add")
def add_student(
    student_id: str = Form(...),
    name: str = Form(...),
    birth_year: int = Form(...),
    major: str = Form(...),
    gpa: float = Form(...),
    class_id: str = Form(...)
):

    db = get_db()

    student = models.Student(
        student_id=student_id,
        name=name,
        birth_year=birth_year,
        major=major,
        gpa=gpa,
        class_id=class_id
    )

    db.add(student)
    db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/delete/{student_id}")
def delete_student(student_id: str):

    db = get_db()

    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()

    db.delete(student)

    db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/edit/{student_id}", response_class=HTMLResponse)
def edit_form(request: Request, student_id: str):

    db = get_db()

    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()

    classes = db.query(models.Class).all()

    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "student": student,
            "classes": classes
        }
    )


@app.post("/update/{student_id}")
def update_student(
    student_id: str,
    name: str = Form(...),
    birth_year: int = Form(...),
    major: str = Form(...),
    gpa: float = Form(...),
    class_id: str = Form(...)
):

    db = get_db()

    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()

    student.name = name
    student.birth_year = birth_year
    student.major = major
    student.gpa = gpa
    student.class_id = class_id

    db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/export")
def export_csv():

    db = get_db()

    students = db.query(models.Student).all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(["student_id","name","birth_year","major","gpa","class_id"])

    for s in students:

        writer.writerow([
            s.student_id,
            s.name,
            s.birth_year,
            s.major,
            s.gpa,
            s.class_id
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=students.csv"
        }
    )