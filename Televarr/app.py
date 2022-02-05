import sys
import os
import json
import requests
import yaml
import playlist


def cont():
    cont = input('\nWould you like to continue? Y or N. ')
    if cont == 'Y' or cont == 'y':
        main()

    elif cont == 'N' or cont == 'n':
        sys.exit()

    else:
        print('Invalid. Continuing.')
        main()


def get_country_file_list():
    country_file_list = []

    for file in os.listdir("./data/countries"):
        country_file_list.append(file.split('.json')[0])

    return country_file_list


def main():
    if 'ez-iptvcat' not in os.getcwd():
        os.chdir("./ez-iptvcat-scraper-master/")

    print("""
	---TELEVARR---

	Please enter the number associated with the action \n	you would like to complete.

	1. Add Channel
	2. List Channels
	3. Add Country 
	4. Reload IPTVCat
	5. Create Playlist
	6. Exit


			""")

    choice = input("Enter Here: ")

    if choice == '1':
        channel = input('Enter Channel Name: ')
        country = input('Enter Channel Country: ')

        if country.lower() not in get_country_file_list():
            print("Invalid Country. Heres a list of valid countries: \n")
            for item in get_country_file_list():
                print(item)

            print("\nIf your country is not listed, add it with number 3 when you continue.")

            cont()

        else:

            with open('../channels.json') as file:
                channels = json.load(file)

            with open('../channels.json', 'w') as file:
                channels.append({'name': channel, 'country': country, 'url': None})
                json.dump(channels, file, ensure_ascii=False, indent=4)

            cont()

    elif choice == '2':
        with open('../channels.json') as file:
            channels = json.load(file)

        for channel in channels:
            print(channel['name'])

        cont()

    elif choice == '3':
        print("List of valid countries: https://iptvcat.com/sitemap")
        country = input("Please enter the country you would like to add: ")
        country = country.replace(" ", "_").lower()
        link = f"https://iptvcat.com/{country}"

        request_response = requests.head(f"{link}\n")
        status_code = request_response.status_code
        website_is_up = status_code == 200

        if website_is_up:
            data = {"name": str(country), "url": str(link)}

            with open('./config.yaml', 'r') as file:
                yaml_data = yaml.load(file, Loader=yaml.Loader)

            for x in yaml_data['sources']:
                if x['name'].lower() == country.lower():
                    print("Country already added!")
                    cont()

            yaml_data['sources'].append(data)


            with open('./config.yaml', 'w') as file:
                yaml.safe_dump(yaml_data, file, indent=4)
                print(f"{country} successfully added!")


        else:
            print("Invalid Country!")
            print("List of valid countries: https://iptvcat.com/sitemap")

        cont()




    elif choice == '4':
        os.system("go run main.go")

    elif choice == '5':
        os.chdir("../")
        playlist.create_playlist()
        cont()

    elif choice == '6':
        print('Exiting...')
        sys.exit()

    else:
        print('Not a valid option.')
        cont()


main()
