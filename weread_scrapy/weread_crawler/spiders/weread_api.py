import json

import scrapy
from scrapy.exceptions import CloseSpider

from weread_crawler.items import WereadApiItem


def split_arg(value):
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def truthy(value):
    return str(value).strip().lower() not in {"0", "false", "no", "off", ""}


class WereadApiSpider(scrapy.Spider):
    name = "weread_api"

    def __init__(
        self,
        book_ids="",
        keywords="",
        modes="monthly,annually",
        crawl_shelf="1",
        crawl_recommend="0",
        crawl_chapters="0",
        crawl_chapter_underlines="0",
        crawl_hot_bookmarks="0",
        crawl_public_reviews="0",
        crawl_review_details="0",
        deep="1",
        max_pages="1",
        count="20",
        chapter_limit="0",
        review_range_limit="0",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.seed_book_ids = split_arg(book_ids)
        self.keywords = split_arg(keywords)
        self.modes = split_arg(modes) or ["monthly", "annually"]
        self.crawl_shelf = truthy(crawl_shelf)
        self.crawl_recommend = truthy(crawl_recommend)
        self.crawl_chapters = truthy(crawl_chapters)
        self.crawl_chapter_underlines = truthy(crawl_chapter_underlines)
        self.crawl_hot_bookmarks = truthy(crawl_hot_bookmarks)
        self.crawl_public_reviews = truthy(crawl_public_reviews)
        self.crawl_review_details = truthy(crawl_review_details)
        self.deep = truthy(deep)
        self.max_pages = max(1, int(max_pages))
        self.count = max(1, int(count))
        self.chapter_limit = max(0, int(chapter_limit))
        self.review_range_limit = max(0, int(review_range_limit))
        self.scheduled_books = set()
        self.scheduled_read_review_ranges = {}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.gateway = crawler.settings.get("WEREAD_API_GATEWAY")
        spider.api_key = crawler.settings.get("WEREAD_API_KEY")
        spider.skill_version = crawler.settings.get("WEREAD_SKILL_VERSION")
        return spider

    def start_requests(self):
        yield from self.build_start_requests()

    async def start(self):
        for request in self.build_start_requests():
            yield request

    def build_start_requests(self):
        if not self.api_key:
            raise CloseSpider("Missing WEREAD_API_KEY. Set env var WEREAD_API_KEY=wrk-xxxxxxxx.")

        if self.crawl_shelf:
            yield self.api_request("/shelf/sync", {}, self.parse_shelf)
            yield self.api_request("/user/notebooks", {"count": self.count}, self.parse_notebooks, {"page": 1})

        for mode in self.modes:
            yield self.api_request("/readdata/detail", {"mode": mode, "baseTime": 0}, self.parse_generic)

        if self.crawl_recommend:
            yield self.api_request("/book/recommend", {"count": self.count}, self.parse_recommend)

        for keyword in self.keywords:
            params = {"keyword": keyword, "scope": 10, "count": self.count, "maxIdx": 0}
            yield self.api_request("/store/search", params, self.parse_search, {"keyword": keyword, "page": 1})

        for book_id in self.seed_book_ids:
            yield from self.schedule_book(book_id)

    def api_request(self, api_name, params, callback, context=None):
        body = {"api_name": api_name, "skill_version": self.skill_version}
        body.update(params)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        return scrapy.Request(
            self.gateway,
            method="POST",
            body=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            callback=callback,
            errback=self.errback_api,
            meta={
                "api_name": api_name,
                "request_params": body,
                "context": context or {},
            },
            dont_filter=True,
        )

    def decode_response(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise CloseSpider(f"Invalid JSON from {response.meta.get('api_name')}: {exc}") from exc

        if data.get("upgrade_info"):
            raise CloseSpider(f"WeRead API requires upgrade: {data['upgrade_info']}")

        errcode = data.get("errcode")
        if errcode not in (None, 0):
            self.logger.warning("API %s returned errcode=%s body=%s", response.meta.get("api_name"), errcode, data)
        return data

    def make_item(self, response, data):
        return WereadApiItem(
            api_name=response.meta["api_name"],
            request_params=response.meta["request_params"],
            response_body=data,
            context=response.meta.get("context", {}),
        )

    def parse_generic(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)

    def parse_shelf(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)
        for book in data.get("books") or []:
            book_id = book.get("bookId")
            if book_id:
                yield from self.schedule_book(book_id)

    def parse_notebooks(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)

        for item in data.get("books") or []:
            book_id = item.get("bookId") or (item.get("book") or {}).get("bookId")
            if book_id:
                yield from self.schedule_book(book_id)

        context = response.meta.get("context", {})
        page = int(context.get("page", 1))
        books = data.get("books") or []
        if data.get("hasMore") and page < self.max_pages and books:
            last_sort = books[-1].get("sort")
            if last_sort:
                yield self.api_request(
                    "/user/notebooks",
                    {"count": self.count, "lastSort": last_sort},
                    self.parse_notebooks,
                    {"page": page + 1},
                )

    def parse_search(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)

        for result in data.get("results") or []:
            book_id = self.extract_book_id(result)
            if book_id:
                yield from self.schedule_book(book_id)

        context = response.meta.get("context", {})
        page = int(context.get("page", 1))
        params = response.meta["request_params"]
        if data.get("hasMore") and page < self.max_pages:
            yield self.api_request(
                "/store/search",
                {
                    "keyword": params.get("keyword"),
                    "scope": params.get("scope", 10),
                    "count": params.get("count", self.count),
                    "maxIdx": int(params.get("maxIdx") or 0) + int(params.get("count") or self.count),
                },
                self.parse_search,
                {"keyword": params.get("keyword"), "page": page + 1},
            )

    def parse_recommend(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)
        for book in data.get("books") or []:
            book_id = book.get("bookId")
            if book_id:
                yield from self.schedule_book(book_id)

    def parse_chapterinfo(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)
        if not self.deep or not self.crawl_chapter_underlines:
            return

        book_id = data.get("bookId")
        chapters = data.get("chapters") or []
        if self.chapter_limit:
            chapters = chapters[: self.chapter_limit]
        for chapter in chapters:
            chapter_uid = chapter.get("chapterUid")
            if book_id and chapter_uid:
                yield self.api_request(
                    "/book/underlines",
                    {"bookId": book_id, "chapterUid": chapter_uid},
                    self.parse_generic,
                    {"book_id": book_id, "chapter_uid": chapter_uid},
                )

    def parse_bestbookmarks(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)
        if not self.deep or not self.review_range_limit:
            return

        book_id = data.get("bookId") or response.meta["request_params"].get("bookId")
        grouped = {}
        for item in (data.get("items") or [])[: self.review_range_limit]:
            chapter_uid = item.get("chapterUid")
            range_text = item.get("range")
            if not (book_id and chapter_uid and range_text):
                continue
            key = (book_id, chapter_uid)
            grouped.setdefault(key, []).append(
                {"range": range_text, "maxIdx": 0, "count": min(self.count, 20), "synckey": 0}
            )

        for (range_book_id, chapter_uid), reviews in grouped.items():
            seen_count = self.scheduled_read_review_ranges.get(range_book_id, 0)
            if seen_count >= self.review_range_limit:
                continue
            reviews = reviews[: self.review_range_limit - seen_count]
            self.scheduled_read_review_ranges[range_book_id] = seen_count + len(reviews)
            yield self.api_request(
                "/book/readreviews",
                {"bookId": range_book_id, "chapterUid": chapter_uid, "reviews": reviews},
                self.parse_readreviews,
                {"book_id": range_book_id, "chapter_uid": chapter_uid},
            )

    def parse_review_list(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)

        for entry in data.get("reviews") or []:
            review_id = ((entry.get("review") or {}).get("reviewId"))
            if self.crawl_review_details and review_id:
                yield self.api_request(
                    "/review/single",
                    {"reviewId": review_id, "commentsCount": 10, "likesCount": 10},
                    self.parse_generic,
                    {"review_id": review_id},
                )

        context = response.meta.get("context", {})
        page = int(context.get("page", 1))
        params = response.meta["request_params"]
        if data.get("reviewsHasMore") and page < self.max_pages:
            yield self.api_request(
                "/review/list",
                {
                    "bookId": params.get("bookId"),
                    "reviewListType": params.get("reviewListType", 0),
                    "count": params.get("count", self.count),
                    "maxIdx": int(params.get("maxIdx") or 0) + int(params.get("count") or self.count),
                    "synckey": data.get("synckey", params.get("synckey", 0)),
                },
                self.parse_review_list,
                {"book_id": params.get("bookId"), "page": page + 1},
            )

    def parse_mine_reviews(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)

        for entry in data.get("reviews") or []:
            review_id = entry.get("reviewId")
            if self.crawl_review_details and review_id:
                yield self.api_request(
                    "/review/single",
                    {"reviewId": review_id, "commentsCount": 10, "likesCount": 10},
                    self.parse_generic,
                    {"review_id": review_id},
                )

        context = response.meta.get("context", {})
        page = int(context.get("page", 1))
        params = response.meta["request_params"]
        if data.get("hasMore") and page < self.max_pages and data.get("synckey"):
            yield self.api_request(
                "/review/list/mine",
                {"bookid": params.get("bookid"), "count": params.get("count", self.count), "synckey": data["synckey"]},
                self.parse_mine_reviews,
                {"book_id": params.get("bookid"), "page": page + 1},
            )

    def parse_readreviews(self, response):
        data = self.decode_response(response)
        yield self.make_item(response, data)

        for block in data.get("reviews") or []:
            for entry in block.get("pageReviews") or []:
                review_id = entry.get("reviewId")
                if self.crawl_review_details and review_id:
                    yield self.api_request(
                        "/review/single",
                        {"reviewId": review_id, "commentsCount": 10, "likesCount": 10},
                        self.parse_generic,
                        {"review_id": review_id},
                    )

    def schedule_book(self, book_id):
        if not book_id or book_id in self.scheduled_books:
            return
        self.scheduled_books.add(book_id)

        yield self.api_request("/book/info", {"bookId": book_id}, self.parse_generic, {"book_id": book_id})
        if not self.deep:
            return

        if self.crawl_chapters or self.crawl_chapter_underlines:
            yield self.api_request("/book/chapterinfo", {"bookId": book_id}, self.parse_chapterinfo, {"book_id": book_id})
        yield self.api_request("/book/getprogress", {"bookId": book_id}, self.parse_generic, {"book_id": book_id})
        yield self.api_request("/book/bookmarklist", {"bookId": book_id}, self.parse_generic, {"book_id": book_id})
        yield self.api_request("/review/list/mine", {"bookid": book_id, "count": self.count}, self.parse_mine_reviews, {"book_id": book_id, "page": 1})
        if self.crawl_hot_bookmarks:
            yield self.api_request("/book/bestbookmarks", {"bookId": book_id, "chapterUid": 0}, self.parse_bestbookmarks, {"book_id": book_id})
        if self.crawl_public_reviews:
            yield self.api_request("/review/list", {"bookId": book_id, "count": self.count, "maxIdx": 0}, self.parse_review_list, {"book_id": book_id, "page": 1})

        if self.crawl_recommend:
            yield self.api_request("/book/similar", {"bookId": book_id, "count": self.count}, self.parse_generic, {"book_id": book_id})

    def extract_book_id(self, obj):
        if not isinstance(obj, dict):
            return None
        for key in ("bookId", "book_id"):
            if obj.get(key):
                return obj[key]
        for key in ("book", "bookInfo", "info"):
            nested = obj.get(key)
            if isinstance(nested, dict):
                value = self.extract_book_id(nested)
                if value:
                    return value
        return None

    def errback_api(self, failure):
        request = failure.request
        self.logger.error("Request failed api=%s params=%s error=%s", request.meta.get("api_name"), request.meta.get("request_params"), failure.value)
