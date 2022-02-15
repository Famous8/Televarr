import json
import re

import yaml


def create_playlist():
	with open('./channels.yaml') as file:
		yaml_data = yaml.load(file, Loader=yaml.Loader)

	with open('./blacklist.yaml') as file:
		blacklist = yaml.load(file, Loader=yaml.Loader)['blacklist']

	for x in yaml_data['channels']:
		link = None
		path = f"./ez-iptvcat-scraper-master/data/countries/{x['country'].lower()}.json"

		with open(path) as file:
			iptvcat = json.load(file)

		for y in iptvcat:
			liveliness = int(y['liveliness'])
			status = y['status']
			result = re.search(rf"\b{x['name'].lower().strip()}\b", y['channel'].lower())

			if result != None and liveliness > 95 and status == 'online' and y['link'] not in blacklist:
				link = y['link']
				x['url'] = link
				break

		if link == None:
			print(f"Channel {x['name']} Not Found.")
			x['url'] = None

	with open('./channels.yaml', 'w') as file:
		yaml.safe_dump(yaml_data, file, indent=4)

	with open("./iptv.m3u", "w") as file:
		file.truncate(0)
		file.write('#EXTM3U')

		for channel in yaml_data['channels']:
			if not channel['url']:
				pass

			else:
				file.write(f"\n#EXTINF:-1, {channel['name']} \n{channel['url']}")

if __name__ == '__main__':
	create_playlist()