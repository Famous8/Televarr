import json, re

with open('./channels.json') as file:
	channels = json.load(file)


for x in channels:
	link = None
	path = f"./ez-iptvcat-scraper-master/data/countries/{x['country']}.json"

	with open(path) as file:
		iptvcat = json.load(file) 

	for y in iptvcat:
		liveliness = int(y['liveliness'])
		status = y['status']
		result = re.search(rf"\b{x['name'].lower().strip()}\b", y['channel'].lower())

		if result != None and liveliness > 95 and status == 'online':
			link = y['link']
			x['url'] = link
			break

	if link == None:
		print(f"Channel {x['name']} Not Found.")
		x['url'] = None

with open('./channels.json', 'w') as file:
	json.dump(channels, file, ensure_ascii=False, indent=4)

with open("./iptv.m3u", "w") as file:
	file.truncate(0)
	file.write('#EXTM3U')

	for channel in channels:
		if not channel['url']:
			pass

		else:
			file.write(f"\n#EXTINF:-1, {channel['name']} \n{channel['url']}")

