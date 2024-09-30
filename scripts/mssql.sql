create table dbo.incremental_data
(
    id int,
    data varchar(max),
    modified datetime
);

select * from dbo.incremental_data;

create table dbo.full_data_airflow
(
    id int,
    data varchar(max)
);
select * from dbo.full_data_airflow;