Драйвер postgresql: https://jdbc.postgresql.org/download/ (просто новую версию для 8 жабы)
Драйвер для mssql: https://learn.microsoft.com/ru-ru/sql/connect/jdbc/download-microsoft-jdbc-driver-for-sql-server?view=sql-server-ver16
Драйвер для mysql: https://dev.mysql.com/downloads/connector/j/


Настройки подключения PostgreSQL:
Строка подключения: jdbc:postgresql://postgres:5432/DWH
Наименование класса драйвера: org.postgresql.Driver

Настройки подключения MSSQL:
Строка подключения: jdbc:sqlserver://mssql;encrypt=true;databaseName=master;trustServerCertificate=true;
Наименование класса драйвера: com.microsoft.sqlserver.jdbc.SQLServerDriver

Настройки подключения MySql:
Строка подключения: jdbc:sqlserver://mssql;encrypt=true;databaseName=master;trustServerCertificate=true;
Наименование класса драйвера: com.mysql.jdbc.Driver