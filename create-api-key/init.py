import glob
import json
import os

import requests
from termcolor import colored

# Create admin api key
create_api_key_body = {
	"name": "admin-key",
	"role": "Admin"
}
print(colored('create new admin key', 'green'))
ret = requests.post("http://admin:mamboserver@grafana:3000/api/auth/keys", data=create_api_key_body)
data = ret.json()
INFLUXDB_PORT = os.environ.get("INFLUXDB_PORT", "")
INFLUXDB_SERVER = os.environ.get("INFLUXDB_SERVER", "")
INFLUXDB_NAME = os.environ.get("INFLUXDB_NAME", "")
INFLUXDB_USERNAME = os.environ.get("INFLUXDB_USERNAME", "")
INFLUXDB_PASSWORD = os.environ.get("INFLUXDB_PASSWORD", "")

print(colored(INFLUXDB_PORT, 'red'))
key = data.get("key", "")
print(colored('admin key %s' % key, 'blue'))

headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": "Bearer %s" % key
}

# Create new folder
create_folder_body = {
	"title": "video_insight"
}

print(colored('create new folder video_insight', 'green'))
ret = requests.post("http://grafana:3000/api/folders", headers=headers, data=json.dumps(create_folder_body))

data = ret.json()
folder_id = data.get("id", "")

print(colored('folder id %s' % folder_id, 'blue'))

# Replace makefile config
with open("/makefile/deploy", "r") as f:
	newText = f.read().replace("GRAFANA_API_KEY?=", "GRAFANA_API_KEY?=%s" % key)
	newText = newText.replace("GRAFANA_FOLDER_ID?=", "GRAFANA_FOLDER_ID?=%s" % folder_id)

with open("/makefile/deploy", "w") as f:
	f.write(newText)

# Create data source
data_sources = [
	{
		"name": "prometheus",
		"type": "prometheus",
		"url": "http://127.0.0.1:9090",
		"access": "proxy",
		"basicAuth": False
	},
	{
		"name": "influxdb",
		"type": "influxdb",
		"url": "http://%s:%s" % (INFLUXDB_SERVER, INFLUXDB_PORT),
		"access": "proxy",
		"basicAuth": False,
		"user": INFLUXDB_USERNAME,
		"password": INFLUXDB_PASSWORD,
		"database": INFLUXDB_NAME
	}
]

for item in data_sources:
	ret = requests.post(
		"http://grafana:3000/api/datasources", headers=headers,
		data=json.dumps(item))
	print(colored('create data source %s %s' % (item.get("name"), ret.json()), 'blue'))

# Create alert notification
notifications = [
	{
		"name": "slack-alert",
		"type": "slack",
		"ifDefault": True,
		"settings": {
			"url": "https://hooks.slack.com/services/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"
		}
	}
]

for notification in notifications:
	ret = requests.post(
		"http://grafana:3000/api/alert-notifications", headers=headers,
		data=json.dumps(notification))
	print(
		colored('create alert notification %s %s' % (notification.get("name"), ret.json()), 'blue'))


dashboard_ids = {}
for filename in glob.iglob("/dashboard/*.json"):
	print(filename)
	with open(filename) as f:
		dashboard = json.load(f)

	filename = filename.split("/")[-1]
	create_dashboard = {
		"dashboard": dashboard,
		"folderId": 0
	}

	ret = requests.post(
		"http://grafana:3000/api/dashboards/db", headers=headers,
		data=json.dumps(create_dashboard))
	data = ret.json()
	print("create dashboard %s %s", filename, data)
	dashboard_id = data.get("id", None)
	if dashboard_id:
		dashboard_ids[filename] = dashboard_id

for filename in glob.iglob("/dashboard/update/*"):
	print(filename)
	root_filename = filename.split("/")[-1]
	dashboard_id = dashboard_ids.get(root_filename, None)
	if dashboard_id:
		with open(filename) as f:
			dashboard_update = json.load(f)
		update_dashboard_body = {
			"id": dashboard_id,
			"dashboard": dashboard_update
		}
