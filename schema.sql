drop database if exists marc1_testing;
CREATE DATABASE marc1_testing;
USE marc1_testing;

create table developer_info
(
	uuid varchar(64) not null
		primary key,
	api_key varchar(64) not null,
	modified_at timestamp default CURRENT_TIMESTAMP null,
	constraint developer_info_api_key_uindex
		unique (api_key)
);

create table form_info
(
	uuid varchar(64) not null,
	form_id varchar(64) not null,
	modified_at timestamp default CURRENT_TIMESTAMP null,
	primary key (form_id, uuid)
);


create table form_column_mapper
(
	form_id varchar(64) not null,
	field_name varchar(128) not null,
	field_type varchar(32) not null,
	expected_values text null,
	modified_at timestamp default CURRENT_TIMESTAMP null,
	primary key (form_id, field_name),
	constraint form_column_mapper_form_info_form_id_fk
		foreign key (form_id) references form_info (form_id)
			on delete cascade
);



create table form_endpoint_mapper
(
	form_id varchar(64) not null,
	accepted_endpoints varchar(512) null,
	modified_at timestamp default CURRENT_TIMESTAMP null,
	id int auto_increment
		primary key,
	constraint form_endpoint_mapper_form_info_form_id_fk
		foreign key (form_id) references form_info (form_id)
			on delete cascade
);

create index form_endpoint_mapper_form_id_accepted_endpoints_index
	on form_endpoint_mapper (form_id, accepted_endpoints);



