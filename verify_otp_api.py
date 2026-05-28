import mysql.connector, os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OTPRequest(BaseModel):
    to_email: str
    otp: str

@app.get("/")
def working():
    return{"message":"api is working"}
    
@app.post("/verify_otp")
def verify_otp(request:OTPRequest):

    to_email = request.to_email
    otp = request.otp

    db = None
    cursor = None
    
    try:
        db = mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database=os.environ.get("DB_DATABASE"),
        port=int(os.environ.get("DB_PORT"))
        )

        cursor = db.cursor()
    
        cursor.execute("""
            delete from email_otp
            where expires_at < NOW()
        """)
        db.commit()

        cursor.execute("""
            select otp from email_otp
            where email=%s and otp=%s
        """,(to_email, otp))
        exist = cursor.fetchone()

        if exist:
            db.commit("""DELETE FROM email_otp WHERE email = %s""",(to_email,))
            db.commit()
            return{"status":"success","message":"otp verified"}
        else:
            return{"status":"error","message":"otp not verified"}
    except mysql.connector.Error as err:
        return {"message": "Database connection failed", "error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    
