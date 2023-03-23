initial:
	python ./manage.py makemigrations
	python ./manage.py migrate
	python ./manage.py collectstatic
	python ./manage.py loaddata ./fixtures/org_positions.json
	python ./manage.py loaddata ./fixtures/replacement_statuses.json

admin:
	python ./manage.py createsuperuser
