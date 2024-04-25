# conda activate webservicep2plending
# uvicorn main:app --reload


from typing import Union  # Import modul Union dari pustaka typing untuk mendefinisikan tipe data gabungan.
from fastapi import FastAPI, Response, Request, HTTPException  # Import kelas FastAPI, Response, Request, dan HTTPException dari modul fastapi.
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware dari modul fastapi.middleware.cors untuk menangani permintaan lintas sumber (CORS).
import sqlite3  # Import modul sqlite3 untuk berinteraksi dengan database SQLite.

app = FastAPI()  # Inisialisasi aplikasi FastAPI.

# Tambahkan middleware CORSMiddleware ke aplikasi FastAPI untuk menangani permintaan lintas sumber (CORS).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fungsi endpoint untuk rute root ("/") yang mengembalikan pesan sambutan.
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Fungsi endpoint untuk mengambil data mahasiswa berdasarkan NIM.
@app.get("/mahasiswa/{nim}")
def ambil_mhs(nim:str):
    return {"nama": "Budi Martami"}

# Fungsi endpoint untuk mengambil data mahasiswa versi kedua berdasarkan NIM.
@app.get("/mahasiswa2/")
def ambil_mhs2(nim:str):
    return {"nama": "Budi Martami 2"}

# Fungsi endpoint untuk mengambil daftar mahasiswa berdasarkan ID provinsi dan angkatan.
@app.get("/daftar_mhs/")
def daftar_mhs(id_prov:str,angkatan:str):
    return {"query":" idprov: {}  ; angkatan: {} ".format(id_prov,angkatan),"data":[{"nim":"1234"},{"nim":"1235"}]}

# Fungsi endpoint untuk inisialisasi database dan tabel.
@app.get("/init/")
def init_db():
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        # Membuat tabel 'mahasiswa' jika belum ada.
        create_table = """ CREATE TABLE mahasiswa(
                ID          INTEGER PRIMARY KEY     AUTOINCREMENT,
                nim         TEXT                    NOT NULL,
                nama        TEXT                    NOT NULL,
                id_prov     TEXT                    NOT NULL,
                angkatan    TEXT                    NOT NULL,
                tinggi_badan  INTEGER
            )  
            """
        cur.execute(create_table)
        con.commit
    except:
        return ({"status":"terjadi error"})  
    finally:
        con.close()
    
    return ({"status":"ok, db dan tabel berhasil dicreate"})

# Definisi model data untuk mahasiswa menggunakan Pydantic.
from pydantic import BaseModel
from typing import Optional

class Mhs(BaseModel):
    nim: str
    nama: str
    id_prov: str
    angkatan: str
    tinggi_badan: Optional[int] | None = None  # Hanya 'tinggi_badan' yang bisa bernilai null.

# Fungsi endpoint untuk menambahkan data mahasiswa ke database.
@app.post("/tambah_mhs/", response_model=Mhs,status_code=201)  
def tambah_mhs(m: Mhs,response: Response, request: Request):
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        # Menambahkan data mahasiswa ke tabel 'mahasiswa'.
        cur.execute("""insert into mahasiswa (nim,nama,id_prov,angkatan,tinggi_badan) values ( "{}","{}","{}","{}",{})""".format(m.nim,m.nama,m.id_prov,m.angkatan,m.tinggi_badan))
        con.commit() 
    except:
        print("oioi error")
        return ({"status":"terjadi error"})   
    finally:  	 
        con.close()
    response.headers["Location"] = "/mahasiswa/{}".format(m.nim) 
    print(m.nim)
    print(m.nama)
    print(m.angkatan)
  
    return m

# Fungsi endpoint untuk menampilkan semua data mahasiswa dari database.
@app.get("/tampilkan_semua_mhs/")
def tampil_semua_mhs():
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        recs = []
        # Mengambil semua data mahasiswa dari tabel 'mahasiswa'.
        for row in cur.execute("select * from mahasiswa"):
            recs.append(row)
    except:
        return ({"status":"terjadi error"})   
    finally:  	 
        con.close()
    return {"data":recs}

# Fungsi endpoint untuk memperbarui data mahasiswa menggunakan metode PUT.
@app.put("/update_mhs_put/{nim}",response_model=Mhs)
def update_mhs_put(response: Response,nim: str, m: Mhs ):
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("select * from mahasiswa where nim = ?", (nim,) )  # Mengecek apakah data mahasiswa dengan NIM yang diberikan ada.
        existing_item = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
    
    if existing_item:  # Jika data ditemukan, lakukan pembaruan.
        print(m.tinggi_badan)
        cur.execute("update mahasiswa set nama = ?, id_prov = ?, angkatan=?, tinggi_badan=? where nim=?", (m.nama,m.id_prov,m.angkatan,m.tinggi_badan,nim))
        con.commit()            
        response.headers["location"] = "/mahasiswa/{}".format(m.nim)
    else:  # Jika data tidak ditemukan, hasilkan error 404.
        print("item not foud")
        raise HTTPException(status_code=404, detail="Item Not Found")
      
    con.close()
    return m

# Definisi model data untuk memperbarui data mahasiswa menggunakan metode PATCH.
class MhsPatch(BaseModel):
    nama: str | None = "kosong"
    id_prov: str | None = "kosong"
    angkatan: str | None = "kosong"
    tinggi_badan: Optional[int] | None = -9999  # Hanya 'tinggi_badan' yang boleh bernilai null atau 0.

# Fungsi endpoint untuk memperbarui data mahasiswa menggunakan metode PATCH.
@app.patch("/update_mhs_patch/{nim}",response_model = MhsPatch)
def update_mhs_patch(response: Response, nim: str, m: MhsPatch ):
    try:
        print(str(m))
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor() 
        cur.execute("select * from mahasiswa where nim = ?", (nim,) )  # Mengecek apakah data mahasiswa dengan NIM yang diberikan ada.
        existing_item = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # Misalnya jika terjadi kesalahan pada database.
    
    if existing_item:  # Jika data ditemukan, lakukan pembaruan.
        sqlstr = "update mahasiswa set "  # Asumsi setidaknya ada satu field yang diperbarui.
        # Memperbarui kolom-kolom yang diberikan dalam model MhsPatch.
        if m.nama != "kosong":
            if m.nama != None:
                sqlstr = sqlstr + " nama = '{}' ,".format(m.nama)
            else:     
                sqlstr = sqlstr + " nama = null ,"
        
        if m.angkatan != "kosong":
            if m.angkatan != None:
                sqlstr = sqlstr + " angkatan = '{}' ,".format(m.angkatan)
            else:
                sqlstr = sqlstr + " angkatan = null ,"
        
        if m.id_prov != "kosong":
            if m.id_prov != None:
                sqlstr = sqlstr + " id_prov = '{}' ,".format(m.id_prov) 
            else:
                sqlstr = sqlstr + " id_prov = null, "     

        if m.tinggi_badan != -9999:
            if m.tinggi_badan != None:
                sqlstr = sqlstr + " tinggi_badan = {} ,".format(m.tinggi_badan)
            else:    
                sqlstr = sqlstr + " tinggi_badan = null ,"

        sqlstr = sqlstr[:-1] + " where nim='{}' ".format(nim)  # Menghapus koma terakhir dan menambahkan kondisi WHERE.
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/mahasiswa/{}".format(nim)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # Jika data tidak ditemukan, hasilkan error 404.
        raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m

# Fungsi endpoint untuk menghapus data mahasiswa berdasarkan NIM.
@app.delete("/delete_mhs/{nim}")
def delete_mhs(nim: str):
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        sqlstr = "delete from mahasiswa  where nim='{}'".format(nim)                 
        print(sqlstr)  # Debug 
        cur.execute(sqlstr)
        con.commit()
    except:
        return ({"status":"terjadi error"})   
    finally:  	 
        con.close()
    
    return {"status":"ok"}