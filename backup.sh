#!/bin/bash

dump_dir=$1
db_password=$2

# current date and time
datetime=$(date +"%F_%H-%M-%S")

# filenames for the dump and archive
sql_filename=${dump_dir}/animehunt_sqldump_${datetime}.sql
archive_filename=${dump_dir}/animehunt_sqldump_${datetime}.7z

# dump command
mysqldump -uroot -p${db_password} animehunt  > ${sql_filename}

# archive command
7z a -t7z ${archive_filename} ${sql_filename}

# clean the raw sql dump
rm ${sql_filename}