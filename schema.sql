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

#CREATE TABLE form_info (
#   id INT(6) ZEROFILL NOT NULL AUTO_INCREMENT,
#   form_id INT(6) ZEROFILL NOT NULL,
#   col varchar(255) NOT NULL,
#   col_type varchar(255) NOT NULL,
#   PRIMARY KEY (id),
#   FOREIGN KEY (form_id) REFERENCES forms(id)
# );

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

CREATE TABLE `form_column_mapper` (
  `form_id` varchar(32) NOT NULL,
  `field_name` varchar(128) NOT NULL,
  `field_type` varchar(32) NOT NULL,
  `expected_values` text,
  `modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`form_id`,`field_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `form_endpoint_mapper` (
  `form_id` varchar(32) NOT NULL,
  `accepted_endpoints` varchar(512) DEFAULT NULL,
  `modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `form_endpoint_mapper_form_id_accepted_endpoints_index` (`form_id`,`accepted_endpoints`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `form_info` (
  `uuid` varchar(32) NOT NULL,
  `form_id` varchar(32) NOT NULL,
  `modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

