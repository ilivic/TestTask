#адрес сервера
host_c = "127.0.0.1"
# имя пользователя для авторизации
user_c = "postgres"
# пароль пользователя
password_c = "9113164242Io"
#база данных с которой будет работать подключение
db_c = "Users"
#порт
port_c = "5432"
#пользователь которого будем проверять 
user_ad = "Grin"
#класс формата таблицы ad_user для удобства деления полученных данных 
class users_c:
    def __init__(self, upn, SAMAccountname, Name, Surname, OtherName, DataLast):
        self._upn = upn
        self.SAMAccountname = SAMAccountname
        self.Name =Name
        self.Surname =Surname
        self.OtherName = OtherName
        self.DataLast = DataLast