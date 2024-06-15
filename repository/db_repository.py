from datetime import date
import sqlite3 as sql

def authenticate(user_id):
	con = sql.connect("retinal_health_diagnostics.db")
	cur = con.cursor()
	cur.execute(f"SELECT UserId, Password, Name FROM RHDUsers where UserId = '{user_id}'")
	users = cur.fetchall()
	con.close()
	return users

def write_to_db(name, gender, age, mobile, email, address, test, result, report):
    
    Date = date.today().strftime("%b-%d-%Y")
    conn = sql.connect('retinal_health_diagnostics.db')
    with conn:
            cursor=conn.cursor()
            
    create_table_sql = '''CREATE TABLE IF NOT EXISTS RHDPatients (
    	PatientId	INTEGER NOT NULL,
    	Name	TEXT NOT NULL,
    	Gender	TEXT NOT NULL,
        Age	INTEGER,
    	MobileNum	NUMERIC,
    	EmailId	TEXT,
    	Address	TEXT,
    	Test	TEXT NOT NULL,
    	DiagnosisResult	TEXT,
    	Report	BLOB,
        TestDTM	TEXT,
    	PRIMARY KEY(PatientId AUTOINCREMENT)
    );'''
    
    insert_sql = '''INSERT INTO RHDPatients 
    (Name, Gender, Age, MobileNum, EmailId, Address, Test, DiagnosisResult, Report, TestDTM)
    VALUES (?,?,?,?,?,?,?,?,?,?)
    '''
    
    cursor.execute(create_table_sql)
    cursor.execute(insert_sql,(name,gender,age,mobile,email,address,test,result,report,Date))
    conn.commit()


def retrieveReport(name):
	con = sql.connect("Diabetic Retinopathy.db")
	cur = con.cursor()
	cur.execute("SELECT DR_Test, DR_Severity FROM DR_Patients_Details where Full_Name= '%s'" %name)
	details = cur.fetchall()
	con.close()
	return details
