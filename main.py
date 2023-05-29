import requests
import time

from bs4 import BeautifulSoup
import pandas as pd
from requests_html import HTMLSession

def has_partial_class(tag, partial_class):
    return any(partial_class in class_name for class_name in tag.get("class", []))

def get_entry(set, selector, element=False):
    entry = set.find_all(lambda tag: has_partial_class(tag, selector))
    if len(entry) > 0:
        if element:
            entry = entry[0]
        else:
            entry = entry[0].text.strip()
    else:
        entry = None
    return entry

def get_entries(username):
    session = HTMLSession()
    page = 1
    entries = []

    while True:
        url = f"https://www.senscritique.com/{username}/collection?page={page}"
        response = session.get(url, timeout=10)
        response.html.render()
        # time.sleep(1)
        list = BeautifulSoup(response.html.html, "html.parser")

        movies = list.findAll("div", {"data-testid": "product-list-item"})
        if len(movies) == 0:
            break

        for movie in movies:

            # Text__SCText-sc-1aoldkr-0 Link__SecondaryLink-sc-1v081j9-1 kcGHBE jacWTu ProductListItem__StyledProductTitle-sc-1jkxxpj-3 dBFYVt
            e_title = get_entry(movie, "ProductTitle", element=True)
            link = e_title["href"]
            title = e_title.text.strip()
            if '(' in title:
                year = title[-5:-1]
                title = title[:-6].strip()

            # Text__SCText-sc-1aoldkr-0 ProductListItem__OriginalTitle-sc-1jkxxpj-4 gATBvH cWqDBb
            original_title = get_entry(movie, "OriginalTitle")

            # Text__SCText-sc-1aoldkr-0 Creators__Text-sc-io0fr2-0 eWSucP guBoRW ProductListItem__StyledCreators-sc-1jkxxpj-6 ekAZTv
            creators = movie.find_all(lambda tag: has_partial_class(tag, "Creators"))
            director = None
            if len(creators) > 0:
                # Text__SCText-sc-1aoldkr-0 Link__PrimaryLink-sc-1v081j9-0 eWSucP bGxijB
                director = creators[0].find("a", {"data-testid": "link"}).find("span").find("span")
                if director:
                    director = director.text.strip()

            # Rating__MyRating-sc-1b09g9c-1 djmAHg Poster__MyRating-sc-1el6aqm-5 fiCWvZ myRating
            # Rating__ActivityRating-sc-1b09g9c-4 kVBTlj
            my_rating = get_entry(movie, "ActivityRating")

            # global_rating = movie.find("div", {"class": "globalRating"}).text.strip()

            # TODO fetching seen date requires login
            # Text__SCText-sc-1aoldkr-0 Link__SecondaryLink-sc-1v081j9-1 kcGHBE jacWTu ProductListItem__StyledProductTitle-sc-1jkxxpj-3 dBFYVt
            # page_url = f"https://www.senscritique.com{link}"
            # page_response = session.get(page_url, timeout=10)
            # page_response.html.render()
            # time.sleep(3)
            # page = BeautifulSoup(page_response.html.html, "html.parser")

            # # Text__SCText-sc-1aoldkr-0 ActionButton__Label-sc-hfjkty-0 gATBvI fXQFkX
            # # find all
            # seen = page.find_all(lambda tag: has_partial_class(tag, "ActionButton__Label"))
            # if len(seen) > 0:
            #     print(seen)
            #     # find the one with the text "Vu le " + date
            #     seen = [s for s in seen if "Vu le" in s.text]
            #     if len(seen) > 0:
            #         print(seen)
            #         seen = seen[0].text.strip()
            #         seen = seen[6:]
            #         seen = seen[:-1]
            #     else:
            #         seen = None
            # else:
            #     seen = None

            entry = {
                "title": title,
                "original_title": original_title,
                "director": director,
                "year": year,
                "my_rating": my_rating,
                # "global_rating": global_rating,
                # "seen": seen,
            }
            print(entry)
            entries.append(entry)

        page += 1
        # break

    return entries

def save_to_csv(collection, output_file):
    df = pd.DataFrame(collection)
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    username = input("Enter your SensCritique username: ")
    collection = get_entries(username)
    
    output_file = "senscritique.csv"
    save_to_csv(collection, output_file)
    print(f"Saved your watched and to-watch movies to {output_file}.")
