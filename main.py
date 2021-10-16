from collections import Counter
from bs4 import BeautifulSoup
import requests
import json

# Author: Jacob Groves
# Produce as part of the interview process for CFCUnderwriting.


def scrape(webpage_url):
    # This function will return a set of EXTERNAL URLs scraped from webpageURL
    links = set()

    # Request data from the url using the Requests library, and parse the content to a list of tags.
    webpage = requests.get(webpage_url)
    content = BeautifulSoup(webpage.text, "lxml")

    # For each tag, if it has a url, append the url to the list.
    # Resources can be referenced from many attributes, including but not
    # limited to: href, src, style, content and xmlns.
    for tag in content.find_all():

        # Urls beginning with '/', '#', 'javascript' or containing 'cfcunderwriting.com' are NOT external
        href = tag.get("href")
        if href is not None:
            if str(href)[0] != '/' \
                    and str(href)[0] != '#' \
                    and not str(href) in webpage_url \
                    and str(href)[0:10] != "javascript":
                links.add(href)

        # Urls beginning with '/' or containing 'cfcunderwriting.com' are NOT external
        src = tag.get("src")
        if src is not None:
            if str(src)[0] != '/' and not str(xmlns) in webpage_url:
                links.add(src)

        # Urls containing 'cfcunderwriting.com' are NOT external
        xmlns = tag.get("xmlns")
        if xmlns is not None:
            if not str(xmlns) in webpage_url:
                links.add(xmlns)

        # Urls containing 'cfcunderwriting.com' are NOT external
        # The content attribute can be used for any text, therefore
        # we omit anything not starting with 'http'
        content = tag.get("content")
        if content is not None:
            if str(content)[0:4] == 'http' and not str(content) in webpage_url:
                links.add(content)

        # The style tag only contains urls in the case of a background image
        style = tag.get("style")
        if style is not None:
            if str(style)[0:16] == 'background-image':
                links.add(str(style)[23:len(style) - 3])

    return links


def write_links_to_json(links):
    data = {'links': []}
    for _ in range(len(links)):
        data['links'].append(links.pop())
    with open('links.json', 'w') as file:
        json.dump(data, file)


def locate_privacy_policy(webpage_url):
    webpage = requests.get(webpage_url)
    content = BeautifulSoup(webpage.text, "lxml")
    links = content.find_all('a')
    for link in links:
        if link.get('title') == "Privacy policy":
            return webpage_url + link.get('href')


def write_word_count_to_json(webpage_url):
    # request the site data, strip away the html, gather the words in a list.
    webpage = requests.get(webpage_url)
    content = BeautifulSoup(webpage.text, "lxml")
    content = content.text.replace("\n", " ").lower()
    words = []
    current_word = ""
    for char in content:
        if not (('a' <= char <= 'z') or ('A' <= char <= 'Z')):
            if len(current_word) > 0:
                words.append(current_word)
                current_word = ""
            continue
        current_word += char
    # now count the wordcount using the Counter() collection.
    counted_words = Counter(words)
    # then print to json file
    data = {'words': []}
    for _ in range(len(counted_words)):
        data['words'].append(counted_words.popitem())
    with open('words.json', 'w') as file:
        json.dump(data, file)


if __name__ == '__main__':

    # Part 1: Scrape the index webpage hosted at `cfcunderwriting.com`
    scrapedLinks = scrape('https://cfcunderwriting.com')

    # Part 2: Writes a list of *all externally loaded resources* (e.g. images/scripts/fonts not hosted
    # on cfcunderwriting.com) to a JSON output file
    write_links_to_json(scrapedLinks)

    # Part 3: Enumerates the page's hyperlinks and identifies the location of the "Privacy Policy" page
    policyURL = locate_privacy_policy('https://cfcunderwriting.com')

    # Part 4:  Use the privacy policy URL identified in step 3 and scrape the pages content.
    # Produce a case-insensitive word frequency count for all of the visible text on the page.
    # Your frequency count should also be written to a JSON output file.
    write_word_count_to_json(policyURL)
