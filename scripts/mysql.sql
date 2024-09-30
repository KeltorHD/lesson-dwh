create table incremental_data
(
    id int,
    data text,
    modified datetime
);

select * from incremental_data;


create table incremental_data_airflow
(
    id int,
    data text,
    modified datetime
);
select * from incremental_data_airflow;