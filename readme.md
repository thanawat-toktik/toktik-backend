# TokTik Backend

Yes. Also, use `poetry`

To run, run:

```sh
poetry update
poetry shell
./manage.py migrate
./manage.py runserver
```

# Database
(Currently using PostgresQL)

## Set up
Requires the following library in order for django to work with database:
```sh
pip3 install psycopg
```

## Make changes
Whenever creating a new table / making changes to the pre-existing tables
```sh
# create a migration file 
# (used for telling django what has been changed)
# can specify which app to migrate
python manage.py makemigrations [APP]
```

When there's a new migration file / when never set up db before:
```sh
# apply the changes found in new migration files 
# to the currently connected database
python manage.py migrate
```
