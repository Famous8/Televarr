package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"regexp"
	"strings"

	app "iptvcat-scraper/pkg"

	"github.com/gocolly/colly"
)

const aHref = "a[href]"

func downloadFile(filepath string, url string) (err error) {
	fmt.Println("downloadFile from ", url, "to ", filepath)

	// Create the file
	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()

	// Get the data
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Check server response
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("bad status: %s", resp.Status)
	}

	// Writer the body to file
	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return err
	}

	return nil
}

func getUrlFromFile(filepath string, origUrl string) (string, error) {
	f, err := os.Open(filepath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	// Splits on newlines by default.
	scanner := bufio.NewScanner(f)

	line := 1
	// https://golang.org/pkg/bufio/#Scanner.Scan
	for scanner.Scan() {
		if strings.HasPrefix(strings.ToLower(scanner.Text()), "http") {
			return scanner.Text(), nil
		}
		line++
	}

	if err := scanner.Err(); err != nil {
		// Handle the error
	}

	return origUrl, err
}

func checkNestedUrls() {
	fmt.Println("checkNestedUrls()")

	converted_urls := map[string]string{}
	ignored := 0
	processed := 0

	for _, stream := range app.Streams.All {
		url_lower := strings.ToLower(stream.Link)

		if strings.Contains(url_lower, "list.iptvcat.com") {
			if _, ok := converted_urls[url_lower]; ok {
				// stream.Link = converted_urls[url_lower]
				ignored++
				fmt.Println(">>> SKIP DUPLICATE: ", ignored)
				continue
			}

			const tmpFile = "tmp.m3u8"
			// Download the file
			downloadFile(tmpFile, stream.Link)

			// Get the Url
			newUrl, err := getUrlFromFile(tmpFile, stream.Link)
			if err != nil {
				fmt.Println(err)
				//return
			}
			//fmt.Println("newUrl found in link: ", newUrl)
			stream.Link = newUrl
			converted_urls[url_lower] = newUrl

			processed++

			// Delete the file
			err2 := os.Remove(tmpFile)
			if err2 != nil {
				fmt.Println(err2)
				return
			}

		} else {
			fmt.Println("no m3u8 found in link: ", stream.Link)
		}
	}

	fmt.Println("### MAP ", converted_urls)
	fmt.Println("### ignored ", ignored)
	fmt.Println("### processed ", processed)

}

func writeToFile() {
	streamsAll, err := json.MarshalIndent(app.Streams.All, "", "    ")
	streamsCountry, err := json.MarshalIndent(app.Streams.ByCountry, "", "    ")
	if err != nil {
		fmt.Println("error:", err)
	}

	os.MkdirAll("data/countries", os.ModePerm)

	ioutil.WriteFile("data/all-streams.json", streamsAll, 0644)
	ioutil.WriteFile("data/all-by-country.json", streamsCountry, 0644)
	for key, val := range app.Streams.ByCountry {
		// streamsCountry, err := json.Marshal(val)
		streamsCountry, err := json.MarshalIndent(val, "", "    ")
		if err != nil {
			fmt.Println("error:", err)
		}
		ioutil.WriteFile("data/countries/"+key+".json", streamsCountry, 0644)
	}
}

func processUrl(url string, domain string) {
	urlFilters := regexp.MustCompile(url + ".*")
	c := colly.NewCollector(
		colly.AllowedDomains(domain),
		colly.URLFilters(urlFilters),
	)

	c.OnResponse(func(r *colly.Response) {
		fmt.Println("Visited", r.Request.URL)
	})

	c.OnHTML(aHref, app.HandleFollowLinks(c))
	c.OnHTML(app.GetStreamTableSelector(), app.HandleStreamTable(c))

	c.OnScraped(func(r *colly.Response) {
		fmt.Println("Finished", r.Request.URL)
	})

	c.OnError(func(r *colly.Response, err error) {
		fmt.Printf("Error: %d %s\n", r.StatusCode, r.Request.URL)
	})

	c.Visit(url)
	c.Wait()
	checkNestedUrls()
	writeToFile()
}

func main() {
	const iptvCatDomain = "iptvcat.com"

	urlList := [...]string{
		"https://iptvcat.com/united_kingdom",
		"https://iptvcat.com/canada",
		"https://iptvcat.com/united_states_of_america",
		"https://iptvcat.com/pakistan",
		"https://iptvcat.com/undefined",
	}

	for _, element := range urlList {
		processUrl(element, iptvCatDomain)
	}

}
