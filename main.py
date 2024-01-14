#подключение библиотеки для работы с psql
import psycopg2 
#подключение библиотеки для получения текущего время
import datetime
#подключение библиотеки для работы с powershell
import subprocess
#импорт переменных из файла config.py для экономии места и потенциальной смены сервера и пользователя проверки
from config import host_c, password_c, db_c, user_c, port_c, users_c, user_ad


#переменная для проверки время входа 
_date = "user not"
#блок обработки исключений 
try:
    #создание соединения с сервером
    _connect = psycopg2.connect( 
        host=host_c,
        user=user_c,
        password=password_c,
        database=db_c,
        port=port_c
    )

    #автоматическое сохранение изменений в бд
    _connect.autocommit = True
    
    #получаем список пользователей AD при помощи powershell
    def getUser():
        _answer = subprocess.Popen(['powershell', f'''Get-ADUser -Filter "GivenName -like '{user_ad}*' " -Properties UserPrincipalName , SamAccountName, Name, Surname,LastLogonDate'''], stdout= subprocess.PIPE)
        stdout,stderr = _answer.communicate()
        _strkey=stdout,stderr.__str__
        #создаём перменную типа users_c с делением полученной информации 
        _user= users_c(
            upn=_strkey.__str__().split(':')[11].__str__().split('\\')[0],
            SAMAccountname=_strkey.__str__().split(':')[8].__str__().split('\\')[0],
            Name=_strkey.__str__().split(':')[3].__str__().split('\\')[0],
            Surname=_strkey.__str__().split(':')[10].__str__().split('\\')[0].__str__().split(' ')[2],
            OtherName=_strkey.__str__().split(':')[10].__str__().split('\\')[0].__str__().split(' ')[1],
            DataLast=_strkey.__str__().split(':')[4].__str__().split('\\')[0]+":"+_strkey.__str__().split(':')[5].__str__().split('\\')[0]+":"+_strkey.__str__().split(':')[6].__str__().split('\\')[0]
        )
        return _user

    #выполнение запроса на заполнение базы данных
    with _connect.cursor() as cursor:
       #используем метод для получения данных из ad 
        _getData = getUser()
        #проверяем время последнего входа и был ли вход вообще
        if _getData.DataLast.__str__().split(':')[0] == ' ':
            #если не был отписываем 
            _date = "user not connection"
        else:
            #если был передаём в переменную для записи время из консоли
            _date = _getData.DataLast

        #делаем запрос на проверку есть ли пользователь в базе по данным для входа
        cursor.execute(f"""SELECT "UPN" FROM public."AD_User" WHERE "UPN" = '{_getData._upn}' """)
        _checker = cursor.fetchone() 
        if _checker == None:
            
            # если нет создаём с заданными параметрами 
            cursor.execute(
                 f"""INSERT INTO public."AD_User"("UPN", "SAMAccountname", "Name", "Surname", "OtherName", "LastConnection") VALUES 
                    ('{_getData._upn}', '{_getData.SAMAccountname}', '{_getData.Name}', '{_getData.Surname}', '{_getData.OtherName}', '{_date}');"""
            )
            print ("Insert is ok")
        else:
            
            # если есть то обнавляем время последнего входа и добавляем от какой даты была проверка 
            cursor.execute(
                f"""UPDATE public."AD_User" SET "LastConnection"= '{_date} out {datetime.datetime.now()}' WHERE "UPN" = '{_getData._upn}'"""
            )
            print ("update is ok")
            

# исключение при ошибки выполнения
except Exception as _ex:
    print ('Error',_ex)

#завершающий блок отключения от сервера
finally:
    if _connect:
        _connect.close()
        print('Connection closed')
