-- Создание схемы для промежуточных данных
create schema stg;

-- Загрузка из MS
create table stg.mssql_incremental_data
(
    id int,
    data text,
    modified timestamp
);
select
    coalesce(max(modified), '2000-01-01'::timestamp) as max
from
    stg.mssql_incremental_data;

-- Загрузка из MySql
create table stg.mysql_incremental_data
(
    id int,
    data text,
    modified timestamp
);
select
    coalesce(max(modified), '2000-01-01'::timestamp) as max
from
    stg.mysql_incremental_data;


create table stg.from_csv
(
    id int,
    first text,
    second text
);
select * from stg.from_csv;

create table incremental_data_airflow
(
    id int,
    data text,
    modified timestamp,
    load_dt timestamp
);

create procedure stg.f1()
language plpgsql
as $$
begin

    raise notice 'Факт 1';

end;
$$;

create procedure stg.f2()
language plpgsql
as $$
begin

    raise notice 'Факт 2';

end;
$$;

delete from
    full_data_airflow
where
    (id, load_dt) in
        (
            select
                id, load_dt
            from
                (
                    select
                        *, row_number() over (partition by id order by load_dt desc) as rn
                    from full_data_airflow
                ) as q
            where rn > 1
        );