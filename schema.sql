CREATE DATABASE marc1_db;
USE marc1_db;

CREATE TABLE developers (
  id INT(6) ZEROFILL NOT NULL AUTO_INCREMENT,
  api_key varchar(255) NOT NULL UNIQUE,
  uuid varchar(255) NOT NULL UNIQUE
  PRIMARY KEY (id),
);
