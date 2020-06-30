from django.http import Http404
from django.shortcuts import render
from django.views import View
import json
from django.conf import settings

NEWS_JSON_PATH = settings.NEWS_JSON_PATH

with open(NEWS_JSON_PATH, 'r') as f:
    news = json.load(f)


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

