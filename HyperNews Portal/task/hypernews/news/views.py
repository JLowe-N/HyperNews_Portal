from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.conf import settings
from django import forms
import json
from datetime import datetime
import itertools
from random import randint
from copy import deepcopy

NEWS_JSON_PATH = settings.NEWS_JSON_PATH
def time_strip(datetime):
    # Removes time from a datetime object and returns a string
    return datetime.strftime("%Y-%m-%d")

def load_news():
    global news_JSON, news, headlines, active_links
    with open(NEWS_JSON_PATH, 'r') as f:
        news_JSON = json.load(f)
        print(f"opened file {news_JSON}")
    # Convert all date strings into datetime objects, create list of links
    active_links = []
    news = deepcopy(news_JSON)
    for news_dict in news:
        news_dict["created"] = datetime.strptime(news_dict["created"], "%Y-%m-%d %H:%M:%S")
        active_links.append(news_dict['link'])
    # Order news by datetime object
    news.sort(key=lambda x: x['created'], reverse=True)
    # Reorder list of dicts from JSON file, grouped by Y-M-D date
    headlines = [{'date': date, 'values': list(news_dict)} for date, news_dict in
                 itertools.groupby(news, lambda x: time_strip(x['created']))]
    print(f"returning news_JSON as {news_JSON}")
    return news_JSON, news, headlines, active_links


news_JSON, news, headlines, active_links = load_news()
print(id(news_JSON[0]["created"]), id(news[0]['created']))

def assign_new_link(links_list):
    new_link = randint(1, 99999999)
    while new_link in links_list:
        new_link = randint(1, 99999999)
    return new_link


class CreateNewsForm(forms.Form):
    title = forms.CharField(max_length=50)
    text = forms.CharField(min_length=10)



class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'news/index.html', context={"news": headlines})

class NewsView(View):
    def get(self, request, news_link, *args, **kwargs):
        # Oh, well I guess now I know regular expressions are returned as
        # strings! Oops. JSON dict['link'] is deserialized into an int.
        news_item = None
        for news_dict in news:
            # Converting news_dict['link'] into a string - less chance of an exception
            if str(news_dict["link"]) == news_link:
                news_item = news_dict
        if not news_item:
            raise Http404
        else:
            return render(request, 'news/story.html', context=news_item)


class CreateNewsView(View):
    def get(self, request, *args, **kwargs):
        create_news_form = CreateNewsForm()
        return render(request, 'news/create.html', context={'news_form': create_news_form})

    def post(self, request, *args, **kwargs):
        global news_JSON, news, headlines, active_links
        create_news_form = CreateNewsForm(request.POST)
        print(create_news_form)
        if create_news_form.is_valid():
            data = create_news_form.cleaned_data
            news_dict = {
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'title': data['title'],
                'text': data['text'],
                'link': assign_new_link(active_links)
            }
            news_JSON.append(news_dict)
            with open(NEWS_JSON_PATH, 'wt') as f:
                json.dump(news_JSON, f)
            news_JSON, news, headlines, active_links = load_news()
        return HttpResponseRedirect('/news/')
