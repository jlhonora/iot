#!/bin/bash

psql --file=psql_db_setup.sql
psql -U pgtest2user --file=psql_table_setup.sql pgtest2db
