from database import SessionLocal
import models

db = SessionLocal()

c1 = models.Class(
    class_id="CS01",
    class_name="Computer Science 1",
    advisor="Nguyen Van A"
)

c2 = models.Class(
    class_id="IS01",
    class_name="Information Systems1",
    advisor="Tran Van B"
)

c3 = models.Class(
    class_id="DS01",
    class_name="Data Science1",
    advisor="Nguyen Van C"
)

c4 = models.Class(
    class_id="CE1",
    class_name="Computer Engineering1",
    advisor="Nguyen Van D"
)

db.add(c1)
db.add(c2)
db.add(c3)
db.add(c4)

db.commit()

print("Classes added")