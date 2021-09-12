CREATE DATABASE IF NOT EXISTS db DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE db.users (
     id INT NOT NULL auto_increment, 
     name varchar(20) NOT NULL, 
     email varchar(20) NOT NULL, 
     password char(80) NOT Null, PRIMARY KEY (id) 
     );