import pymysql

try:
    db = pymysql.connect(host='localhost',user='root',password='',database='dhruv')
    db.commit()
    print("Database conneted")
except Exception as e:
    print(e)

cr = db.cursor()

create_table="CREATE TABLE product(id INT PRIMARY KEY AUTO_INCREMENT,name varchar(10),price INT,quantity INT)"

try:
    cr.execute(create_table)
    db.commit()
    print("Maru table banigyu agad vadho :")
except Exception as e:
    print(e)

# insert_data = "INSERT INTO product (name,price,quantity) VALUES ('laptop',1000,5),('headphone',100,9),('glass',10,8)"

# try:
#     cr.execute(insert_data)
#     db.commit()
#     print("Maro data database ma avi gyo :")
# except Exception as e:
#     print(e)

# update_data = "update product set name='mobile',price = '51000' where id=1 "
# try:
#     cr.execute(update_data)
#     db.commit()
#     print("Maro data database update thay gyo")
# except Exception as e:
#     print(e)


delete_data="delete  from product where id=3"
try:
    cr.execute(delete_data)
    db.commit()
    print("Maro data database mathi bhusay gayo che")
except Exception as e:
    print(e)
