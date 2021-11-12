CREATE DATABASE marc1_db;
USE marc1_db;

CREATE TABLE developers (
  id INT(6) ZEROFILL NOT NULL AUTO_INCREMENT,
  api_key varchar(255) NOT NULL UNIQUE,
  uuid varchar(255) NOT NULL UNIQUE,
  PRIMARY KEY (id)
);

CREATE TABLE forms (
  id INT(6) ZEROFILL NOT NULL AUTO_INCREMENT,
  uuid varchar(255) NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (uuid) REFERENCES developers(uuid)
);

CREATE TABLE form_info (
  id INT(6) ZEROFILL NOT NULL AUTO_INCREMENT,
  form_id INT(6) ZEROFILL NOT NULL,
  col varchar(255) NOT NULL,
  col_type varchar(255) NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (form_id) REFERENCES forms(id)
);

CREATE TABLE form_submission (
  id INT(6) ZEROFILL NOT NULL AUTO_INCREMENT,
  form_id INT(6) ZEROFILL NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (form_id) REFERENCES forms(id)
);

CREATE TABLE form_submission_field_entry (
  id INT(6) ZEROFILL NOT NULL AUTO_INCREMENT,
  form_submission_id INT(6) ZEROFILL NOT NULL,
  col varchar(255) NOT NULL,
  col_val varchar(255),
  FOREIGN KEY (form_submission_id) REFERENCES form_submission(id),
  PRIMARY KEY (id)
);

