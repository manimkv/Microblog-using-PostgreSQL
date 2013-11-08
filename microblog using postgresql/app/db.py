import psycopg2
con = psycopg2.connect(database='manimkv') 
cur = con.cursor()
cur.execute("CREATE TABLE blogspot(id serial,author text,post text,day text,time text,comment text)")
con.commit()
con.close()
