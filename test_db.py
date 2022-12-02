from glob_var import Const , db_connect, kafka_connect, minio_connect

conn, cur  = db_connect()
lista = ['Ngáo','Đá']

Insert_event = 'INSERT INTO vcc_plr.ngao_da(name) VALUES(%s)'
for i in lista:
    print(i)
    insert_value = (i,)
    cur.execute(Insert_event, insert_value)
    conn.commit()
