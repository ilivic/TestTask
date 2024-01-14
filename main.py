#библиотека для подключения к pg
import psycopg2
#библиотека для работы с ad 
from ldap3 import Connection, Server
#перемены для удобства работы из файла static.py
from static import server, password, login, get_attribytes,serach, host_c, user_c, password_c, db_c
#блок подключения, с отловом ошибок сделан отдельно для легкости определения проблемы если не достучаться до сервера 
try:
#подключение к AD
    Server = Server(server)
    _ad = Connection(
        server = Server,
        user = login,
       password = password
    )
#подключение к PG
    _db = psycopg2.connect(
       host=host_c,
        user=user_c,
        password=password_c,
        database=db_c,
    )
except Exception as _ex:
     property('connection error', _ex)

#обсновной блок 
try:
#переменные для разрезания строки и устранения логических ошибок при незаполнености информации о пользователе в ad 
    _date = "s"
    _surOtherName = ""
    _upn = ""
#автоматическое сохранение действий в базе данных
    _db.autocommit=True
#ображение к ad получение необходимых атрибутов 
    _ad.bind()
    _ad.search(serach,'(objectCategory=person)','SUBTREE', attributes=get_attribytes)
# в случае если бы update не получился изначально был вариант дропать базу и снова заполнять
#    _db.cursor().execute("""DELETE FROM public."AD_User" """)

#контекс для обращении к бд
    with _db.cursor() as _cursor:
#цикл перебора всех пользователей ad
        for index in _ad.entries:
            _key=2000
            _checker = index['SamAccountName']
            #обращение к бд для сравнения есть ли пользователь уже в базе 
            _cursor.execute(f"""SELECT "Name" FROM public."AD_User" WHERE "SAMAccountname"='{_checker}'""")
            _result = _cursor.fetchone()
           # если пользователь ни разу не логинился то вписывается что он не логинелся, а не 1600 год
            if int(str(index['LastLogon'])[0:4]) < _key:
                _date="User not connection"
            else:
                _date= index['LastLogon']
#если имя не заданно то в поле Name прописывается Not
            if str(index['SN']).replace(" ","") == "[]":
                _surOtherName = "Not Not"
            else:
                _surOtherName = str(index['SN'])
#если у пользователя нет данных для входа формата user@exemp.dc то пишем, что его нет
            if str(index['UserPrincipalName']).replace(" ","") == "[]":
                _upn="Not"
            else:
                _upn=index['UserPrincipalName']
#если в базе не найден пользователь которого не выдала ad то записываем его 
            if _result is None:
                _cursor.execute(f"""INSERT INTO public."AD_User"("UPN", "SAMAccountname", "Name", "Surname", "OtherName", "LastConnection") VALUES 
                        ('{_upn}', '{index['SamAccountName']}', '{index['Name']}', '{_surOtherName.split(' ')[1]}', '{_surOtherName.split(' ')[0]}', '{_date}');""")
                print(f"inser ok: {index['Name']}")
            else:
#если есть такой пользователь обновляем все поля 
                if _result.__str__().split("'")[1] == index['Name']:
                    _cursor.execute(f"""UPDATE public."AD_User" SET "UPN" = '{_upn}', "Name"='{index['Name']}', "Surname"='{_surOtherName.split(' ')[1]}',
                                 "OtherName"='{_surOtherName.split(' ')[0]}', "LastConnection"='{_date}' WHERE "SAMAccountname"='{_checker}'""")
                    print(f"update ok: {_result}")

               
                 
except Exception as _ex:
    print('error',_ex)

finally:
        if _db:
             _db.close()

        print("Script is finish")