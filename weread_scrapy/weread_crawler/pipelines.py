import json

import pymysql


def as_json(value):
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, default=str)


def as_bool(value):
    if value is None:
        return None
    return int(bool(value))


def first_present(*values):
    for value in values:
        if value not in (None, ""):
            return value
    return None


class WereadMysqlPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getdict("WEREAD_MYSQL"))

    def __init__(self, mysql_settings):
        self.mysql_settings = mysql_settings
        self.conn = None

    def open_spider(self, spider=None):
        self.conn = pymysql.connect(
            cursorclass=pymysql.cursors.DictCursor,
            **self.mysql_settings,
        )

    def close_spider(self, spider=None):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider=None):
        api_name = item["api_name"]
        params = item["request_params"]
        data = item["response_body"]
        context = item.get("context") or {}

        try:
            self.insert(
                "api_responses",
                {
                    "api_name": api_name,
                    "request_params": as_json(params),
                    "response_body": as_json(data),
                },
            )

            handler = {
                "/book/info": self.process_book_info,
                "/book/chapterinfo": self.process_chapterinfo,
                "/book/getprogress": self.process_reading_progress,
                "/store/search": self.process_search,
                "/book/recommend": self.process_recommend,
                "/book/similar": self.process_similar,
                "/shelf/sync": self.process_shelf,
                "/user/notebooks": self.process_notebooks,
                "/book/bookmarklist": self.process_bookmarklist,
                "/book/bestbookmarks": self.process_bestbookmarks,
                "/book/underlines": self.process_underlines,
                "/review/list": self.process_review_list,
                "/review/list/mine": self.process_mine_reviews,
                "/review/single": self.process_review_single,
                "/book/readreviews": self.process_readreviews,
                "/readdata/detail": self.process_readdata,
            }.get(api_name)

            if handler:
                handler(data, params, context)

            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        return item

    def insert(self, table, data):
        clean = {k: v for k, v in data.items() if v is not None}
        columns = list(clean)
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        with self.conn.cursor() as cur:
            cur.execute(sql, [clean[col] for col in columns])
            return cur.lastrowid

    def upsert(self, table, data, key_columns):
        clean = {k: v for k, v in data.items() if v is not None}
        if not clean:
            return None
        columns = list(clean)
        placeholders = ", ".join(["%s"] * len(columns))
        update_columns = [col for col in columns if col not in set(key_columns)]
        if update_columns:
            updates = ", ".join(f"{col}=VALUES({col})" for col in update_columns)
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"
        else:
            sql = f"INSERT IGNORE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        with self.conn.cursor() as cur:
            cur.execute(sql, [clean[col] for col in columns])
            return cur.lastrowid

    def select_one(self, sql, args):
        with self.conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchone()

    def process_book_info(self, data, params, context):
        self.upsert_book(data)
        detail = data.get("newRatingDetail")
        if detail and data.get("bookId"):
            self.upsert(
                "book_rating_details",
                {
                    "book_id": data.get("bookId"),
                    "good": detail.get("good"),
                    "fair": detail.get("fair"),
                    "poor": detail.get("poor"),
                    "recent": detail.get("recent"),
                    "deep_v": detail.get("deepV"),
                    "my_rating": detail.get("myRating"),
                    "rating_title": detail.get("title"),
                    "raw": as_json(detail),
                },
                ["book_id"],
            )

    def process_chapterinfo(self, data, params, context):
        book_id = data.get("bookId") or params.get("bookId")
        self.upsert_book({"bookId": book_id})
        self.upsert(
            "chapter_syncs",
            {
                "book_id": book_id,
                "synckey": data.get("synckey"),
                "chapter_update_time": data.get("chapterUpdateTime"),
                "raw": as_json(data),
            },
            ["book_id"],
        )
        for chapter in data.get("chapters") or []:
            chapter_uid = chapter.get("chapterUid")
            if not (book_id and chapter_uid):
                continue
            self.upsert(
                "chapters",
                {
                    "book_id": book_id,
                    "chapter_uid": chapter_uid,
                    "chapter_idx": chapter.get("chapterIdx"),
                    "level": chapter.get("level"),
                    "title": chapter.get("title"),
                    "word_count": chapter.get("wordCount"),
                    "price": chapter.get("price"),
                    "paid": chapter.get("paid"),
                    "is_mp_chapter": chapter.get("isMPChapter"),
                    "update_time": chapter.get("updateTime"),
                    "raw": as_json(chapter),
                },
                ["book_id", "chapter_uid"],
            )
            for anchor in chapter.get("anchors") or []:
                self.upsert(
                    "chapter_anchors",
                    {
                        "book_id": book_id,
                        "chapter_uid": chapter_uid,
                        "anchor": anchor.get("anchor"),
                        "title": anchor.get("title"),
                        "level": anchor.get("level"),
                        "raw": as_json(anchor),
                    },
                    ["book_id", "chapter_uid", "anchor"],
                )

    def process_reading_progress(self, data, params, context):
        book_id = data.get("bookId") or params.get("bookId")
        book = data.get("book") or {}
        self.upsert_book({"bookId": book_id})
        self.upsert(
            "reading_progress",
            {
                "book_id": book_id,
                "app_id": book.get("appId"),
                "book_version": book.get("bookVersion"),
                "review_id": book.get("reviewId"),
                "chapter_uid": book.get("chapterUid"),
                "chapter_idx": book.get("chapterIdx"),
                "chapter_offset": book.get("chapterOffset"),
                "progress": book.get("progress"),
                "reading_time": book.get("readingTime"),
                "start_reading_time": book.get("startReadingTime"),
                "update_time": book.get("updateTime"),
                "synckey": book.get("synckey"),
                "summary": book.get("summary"),
                "repair_offset_time": book.get("repairOffsetTime"),
                "is_start_reading": book.get("isStartReading"),
                "tts_time": book.get("ttsTime"),
                "install_id": book.get("installId"),
                "record_reading_time": book.get("recordReadingTime"),
                "response_timestamp": data.get("timestamp"),
                "raw": as_json(data),
            },
            ["book_id"],
        )

    def process_search(self, data, params, context):
        session_id = self.insert(
            "search_sessions",
            {
                "sid": data.get("sid"),
                "keyword": params.get("keyword"),
                "scope": params.get("scope"),
                "max_idx": params.get("maxIdx"),
                "count_requested": params.get("count"),
                "has_more": data.get("hasMore"),
                "raw": as_json(data),
            },
        )
        for idx, result in enumerate(data.get("results") or [], start=1):
            book = self.extract_book(result)
            if book:
                self.upsert_book(book)
            self.insert(
                "search_results",
                {
                    "search_session_id": session_id,
                    "result_idx": idx,
                    "result_type": result.get("type") if isinstance(result, dict) else None,
                    "book_id": (book or {}).get("bookId"),
                    "title": (book or result or {}).get("title") if isinstance(result, dict) else None,
                    "author": (book or result or {}).get("author") if isinstance(result, dict) else None,
                    "raw": as_json(result),
                },
            )

    def process_recommend(self, data, params, context):
        for rank, book in enumerate(data.get("books") or [], start=1):
            self.upsert_book(book)
            self.insert_recommendation("recommend", None, book, rank, params, data)

    def process_similar(self, data, params, context):
        source_book_id = params.get("bookId")
        for rank, book in enumerate(self.iter_book_like(data), start=1):
            self.upsert_book(book)
            self.insert_recommendation("similar", source_book_id, book, rank, params, data)

    def insert_recommendation(self, source, source_book_id, book, rank, params, raw):
        if not book or not book.get("bookId"):
            return
        self.insert(
            "book_recommendations",
            {
                "source": source,
                "source_book_id": source_book_id,
                "session_id": params.get("sessionId"),
                "max_idx": params.get("maxIdx"),
                "book_id": book.get("bookId"),
                "rank_no": rank,
                "title": book.get("title"),
                "author": book.get("author"),
                "category": book.get("category"),
                "cover": book.get("cover"),
                "intro": book.get("intro"),
                "price": book.get("price"),
                "pay_type": book.get("payType"),
                "type": book.get("type"),
                "raw": as_json(book),
            },
        )

    def process_shelf(self, data, params, context):
        for book in data.get("books") or []:
            book_id = book.get("bookId")
            if not book_id:
                continue
            self.upsert_book(book)
            self.upsert(
                "shelf_books",
                {
                    "book_id": book_id,
                    "finish_reading": book.get("finishReading"),
                    "read_update_time": book.get("readUpdateTime"),
                    "secret": book.get("secret"),
                    "update_time": book.get("updateTime"),
                    "is_top": as_bool(book.get("isTop")),
                    "raw": as_json(book),
                },
                ["book_id"],
            )

        for archive in data.get("archive") or []:
            archive_id = self.upsert_archive(archive)
            for book_id in archive.get("bookIds") or []:
                self.upsert("shelf_archive_books", {"archive_id": archive_id, "book_id": book_id}, ["archive_id", "book_id"])
            for album_id in archive.get("albumIds") or []:
                self.upsert("shelf_archive_albums", {"archive_id": archive_id, "album_id": album_id}, ["archive_id", "album_id"])

        for album in data.get("albums") or []:
            info = album.get("albumInfo") or {}
            extra = album.get("albumInfoExtra") or {}
            album_id = info.get("albumId") or extra.get("albumId")
            if album_id:
                self.upsert(
                    "albums",
                    {
                        "album_id": album_id,
                        "name": info.get("name"),
                        "author_name": info.get("authorName"),
                        "cover": info.get("cover"),
                        "intro": info.get("intro"),
                        "update_time": info.get("updateTime"),
                        "finish_status": info.get("finishStatus"),
                        "type": info.get("type"),
                        "track_count": info.get("trackCount"),
                        "secret": extra.get("secret"),
                        "lecture_paid": extra.get("lecturePaid"),
                        "lecture_read_update_time": extra.get("lectureReadUpdateTime"),
                        "is_top": as_bool(extra.get("isTop")),
                        "raw": as_json(album),
                    },
                    ["album_id"],
                )

        mp = data.get("mp") or {}
        mp_book = mp.get("book") or {}
        if mp_book.get("bookId"):
            self.upsert(
                "mp_collection",
                {
                    "book_id": mp_book.get("bookId"),
                    "show_flag": mp.get("show"),
                    "title": mp_book.get("title"),
                    "cover": mp_book.get("cover"),
                    "secret": mp_book.get("secret"),
                    "pay_type": mp_book.get("payType"),
                    "paid": mp_book.get("paid"),
                    "update_time": mp_book.get("updateTime"),
                    "read_update_time": mp_book.get("readUpdateTime"),
                    "is_top": as_bool(mp_book.get("isTop")),
                    "raw": as_json(mp),
                },
                ["book_id"],
            )

    def process_notebooks(self, data, params, context):
        sync_id = self.insert(
            "notebook_syncs",
            {
                "synckey": data.get("synckey"),
                "total_book_count": data.get("totalBookCount"),
                "total_note_count": data.get("totalNoteCount"),
                "no_book_review_count": data.get("noBookReviewCount"),
                "has_more": data.get("hasMore"),
                "last_sort": params.get("lastSort"),
                "raw": as_json(data),
            },
        )
        for item in data.get("books") or []:
            book = item.get("book") or {"bookId": item.get("bookId")}
            book_id = item.get("bookId") or book.get("bookId")
            if not book_id:
                continue
            self.upsert_book(book)
            self.upsert(
                "notebooks",
                {
                    "book_id": book_id,
                    "notebook_sync_id": sync_id,
                    "review_count": item.get("reviewCount"),
                    "marked_status": item.get("markedStatus"),
                    "reading_progress": item.get("readingProgress"),
                    "note_count": item.get("noteCount"),
                    "bookmark_count": item.get("bookmarkCount"),
                    "sort_value": item.get("sort"),
                    "raw": as_json(item),
                },
                ["book_id"],
            )
            for category in book.get("categories") or []:
                self.upsert_book_category(book_id, category)

    def process_bookmarklist(self, data, params, context):
        book = data.get("book") or {"bookId": params.get("bookId")}
        book_id = book.get("bookId") or params.get("bookId")
        self.upsert_book(book)
        for chapter in data.get("chapters") or []:
            chapter_uid = chapter.get("chapterUid")
            if book_id and chapter_uid:
                self.upsert(
                    "bookmark_chapters",
                    {
                        "book_id": book_id,
                        "chapter_uid": chapter_uid,
                        "chapter_idx": chapter.get("chapterIdx"),
                        "title": chapter.get("title"),
                        "raw": as_json(chapter),
                    },
                    ["book_id", "chapter_uid"],
                )
        for bookmark in data.get("updated") or []:
            bookmark_id = bookmark.get("bookmarkId")
            item_book_id = bookmark.get("bookId") or book_id
            if bookmark_id and item_book_id:
                self.upsert_book({"bookId": item_book_id})
                self.upsert(
                    "user_bookmarks",
                    {
                        "bookmark_id": bookmark_id,
                        "book_id": item_book_id,
                        "chapter_uid": bookmark.get("chapterUid"),
                        "chapter_idx": bookmark.get("chapterIdx"),
                        "range_text": bookmark.get("range"),
                        "mark_text": bookmark.get("markText"),
                        "color_style": bookmark.get("colorStyle"),
                        "type": bookmark.get("type"),
                        "create_time": bookmark.get("createTime"),
                        "raw": as_json(bookmark),
                    },
                    ["bookmark_id"],
                )

    def process_bestbookmarks(self, data, params, context):
        book_id = data.get("bookId") or params.get("bookId")
        self.upsert_book({"bookId": book_id})
        for chapter in data.get("chapters") or []:
            if chapter.get("chapterUid"):
                self.upsert(
                    "bookmark_chapters",
                    {
                        "book_id": chapter.get("bookId") or book_id,
                        "chapter_uid": chapter.get("chapterUid"),
                        "chapter_idx": chapter.get("chapterIdx"),
                        "title": chapter.get("title"),
                        "raw": as_json(chapter),
                    },
                    ["book_id", "chapter_uid"],
                )
        for item in data.get("items") or []:
            bookmark_id = item.get("bookmarkId")
            item_book_id = item.get("bookId") or book_id
            if bookmark_id and item_book_id:
                self.upsert_book({"bookId": item_book_id})
                self.upsert(
                    "best_bookmarks",
                    {
                        "bookmark_id": bookmark_id,
                        "book_id": item_book_id,
                        "user_vid": item.get("userVid"),
                        "chapter_uid": item.get("chapterUid"),
                        "range_text": item.get("range"),
                        "simplified_range": item.get("simplifiedRange"),
                        "traditional_range": item.get("traditionalRange"),
                        "mark_text": item.get("markText"),
                        "total_count": item.get("totalCount"),
                        "synckey": data.get("synckey"),
                        "raw": as_json(item),
                    },
                    ["bookmark_id"],
                )

    def process_underlines(self, data, params, context):
        book_id = data.get("bookId") or params.get("bookId")
        chapter_uid = data.get("chapterUid") or params.get("chapterUid")
        self.upsert_book({"bookId": book_id})
        for item in data.get("underlines") or []:
            if book_id and chapter_uid and item.get("range"):
                self.upsert(
                    "underline_stats",
                    {
                        "book_id": book_id,
                        "chapter_uid": chapter_uid,
                        "range_text": item.get("range"),
                        "count_value": item.get("count"),
                        "score": item.get("score"),
                        "type": item.get("type"),
                        "synckey": data.get("synckey"),
                        "raw": as_json(item),
                    },
                    ["book_id", "chapter_uid", "range_text"],
                )

    def process_review_list(self, data, params, context):
        book_id = params.get("bookId")
        self.upsert_book({"bookId": book_id})
        self.insert(
            "review_list_batches",
            {
                "book_id": book_id,
                "review_list_type": params.get("reviewListType"),
                "synckey": data.get("synckey"),
                "max_idx": params.get("maxIdx"),
                "count_requested": params.get("count"),
                "reviews_has_more": data.get("reviewsHasMore"),
                "reviews_has_5_star": data.get("reviewsHas5Star"),
                "reviews_has_1_star": data.get("reviewsHas1Star"),
                "reviews_has_recent": data.get("reviewsHasRecent"),
                "reviews_cnt": data.get("reviewsCnt"),
                "recent_total_cnt": data.get("recentTotalCnt"),
                "friend_comment_count": data.get("friendCommentCount"),
                "friend_unique_count": data.get("friendUniqueCount"),
                "deep_v_recommend_info": as_json(data.get("deepVRecommendInfo")),
                "deep_v_recommend_value": data.get("deepVRecommendValue"),
                "deep_v_unique_count": data.get("deepVUniqueCount"),
                "raw": as_json(data),
            },
        )
        for entry in data.get("reviews") or []:
            wrapper = entry.get("review") or {}
            review = wrapper.get("review") or {}
            review_id = wrapper.get("reviewId") or review.get("reviewId")
            if review_id:
                review["reviewId"] = review_id
                review["book"] = review.get("book") or {"bookId": book_id}
                self.upsert_review(review, "public_list", wrapper.get("likesCount"), wrapper.get("commentsCount"))

    def process_mine_reviews(self, data, params, context):
        book_id = params.get("bookid")
        self.upsert_book({"bookId": book_id})
        self.insert(
            "personal_review_batches",
            {
                "book_id": book_id,
                "synckey": data.get("synckey"),
                "total_count": data.get("totalCount"),
                "has_more": data.get("hasMore"),
                "removed": as_json(data.get("removed")),
                "raw": as_json(data),
            },
        )
        for entry in data.get("reviews") or []:
            review = entry.get("review") or {}
            review_id = entry.get("reviewId") or review.get("reviewId")
            if review_id:
                review["reviewId"] = review_id
                review["bookId"] = review.get("bookId") or book_id
                self.upsert_review(review, "mine", None, None)

    def process_review_single(self, data, params, context):
        review = data.get("review") or {}
        review["reviewId"] = data.get("reviewId") or params.get("reviewId")
        review["htmlContent"] = first_present(review.get("htmlContent"), data.get("htmlContent"))
        self.upsert_review(review, "single", None, None)
        if review.get("reviewId"):
            self.upsert(
                "review_single_details",
                {
                    "review_id": review.get("reviewId"),
                    "synckey": data.get("synckey"),
                    "html_content": data.get("htmlContent"),
                    "comments": as_json(data.get("comments")),
                    "likes": as_json(data.get("likes")),
                    "raw": as_json(data),
                },
                ["review_id"],
            )

    def process_readreviews(self, data, params, context):
        book_id = data.get("bookId") or params.get("bookId")
        chapter_uid = data.get("chapterUid") or params.get("chapterUid")
        self.upsert_book({"bookId": book_id})
        for block in data.get("reviews") or []:
            range_text = block.get("range")
            if not (book_id and chapter_uid and range_text):
                continue
            self.upsert(
                "read_review_ranges",
                {
                    "book_id": book_id,
                    "chapter_uid": chapter_uid,
                    "range_text": range_text,
                    "bookmark_count": block.get("bookMarkCount"),
                    "max_idx": block.get("maxIdx"),
                    "total_count": block.get("totalCount"),
                    "has_more": block.get("hasMore"),
                    "synckey": block.get("synckey"),
                    "raw": as_json(block),
                },
                ["book_id", "chapter_uid", "range_text"],
            )
            row = self.select_one(
                "SELECT id FROM read_review_ranges WHERE book_id=%s AND chapter_uid=%s AND range_text=%s",
                [book_id, chapter_uid, range_text],
            )
            if not row:
                continue
            range_id = row["id"]
            for entry in block.get("pageReviews") or []:
                review = entry.get("review") or {}
                review_id = entry.get("reviewId") or review.get("reviewId")
                if review_id:
                    review["reviewId"] = review_id
                    review["bookId"] = review.get("bookId") or book_id
                    self.upsert_review(review, "readreviews", entry.get("likesCount"), entry.get("commentsCount"))
                    self.upsert(
                        "read_review_page_reviews",
                        {
                            "read_review_range_id": range_id,
                            "review_id": review_id,
                            "likes_count": entry.get("likesCount"),
                            "comments_count": entry.get("commentsCount"),
                            "raw": as_json(entry),
                        },
                        ["read_review_range_id", "review_id"],
                    )

    def process_readdata(self, data, params, context):
        stat_id = self.insert(
            "reading_stats",
            {
                "mode": params.get("mode", "monthly"),
                "base_time": data.get("baseTime"),
                "read_days": data.get("readDays"),
                "total_read_time": data.get("totalReadTime"),
                "day_average_read_time": data.get("dayAverageReadTime"),
                "compare_value": data.get("compare"),
                "prefer_category_word": data.get("preferCategoryWord"),
                "prefer_time": as_json(data.get("preferTime")),
                "regist_time": data.get("registTime"),
                "wr_read_time": data.get("wrReadTime"),
                "wr_listen_time": data.get("wrListenTime"),
                "rank_info": as_json(data.get("rank")),
                "medals": as_json(data.get("medals")),
                "prefer_author": as_json(data.get("preferAuthor")),
                "prefer_publisher": as_json(data.get("preferPublisher")),
                "read_records_word": data.get("readRecordsWord"),
                "read_distribution_word": data.get("readDistributionWord"),
                "raw": as_json(data),
            },
        )
        for day_timestamp, read_time in (data.get("readTimes") or {}).items():
            self.upsert(
                "reading_stat_daily_times",
                {"reading_stat_id": stat_id, "day_timestamp": int(day_timestamp), "read_time": read_time},
                ["reading_stat_id", "day_timestamp"],
            )
        for rank, item in enumerate(data.get("readLongest") or [], start=1):
            book = item.get("book") or {}
            self.upsert_book(book)
            self.insert(
                "reading_longest_books",
                {
                    "reading_stat_id": stat_id,
                    "book_id": book.get("bookId"),
                    "rank_no": rank,
                    "read_time": item.get("readTime"),
                    "tags": as_json(item.get("tags")),
                    "raw": as_json(item),
                },
            )
        for category in data.get("preferCategory") or []:
            self.insert(
                "reading_prefer_categories",
                {
                    "reading_stat_id": stat_id,
                    "category_id": category.get("categoryId"),
                    "category_title": category.get("categoryTitle"),
                    "parent_category_id": category.get("parentCategoryId"),
                    "parent_category_title": category.get("parentCategoryTitle"),
                    "reading_count": category.get("readingCount"),
                    "reading_time": category.get("readingTime"),
                    "raw": as_json(category),
                },
            )
        for item in data.get("readStat") or []:
            self.insert(
                "reading_stat_items",
                {"reading_stat_id": stat_id, "stat": item.get("stat"), "counts": item.get("counts"), "raw": as_json(item)},
            )
        for item in data.get("preferBooks") or []:
            book = item.get("bookInfo") or {}
            self.upsert_book(book)
            self.insert(
                "reading_prefer_books",
                {
                    "reading_stat_id": stat_id,
                    "type": item.get("type"),
                    "title": item.get("title"),
                    "book_id": book.get("bookId"),
                    "reason": item.get("reason"),
                    "raw": as_json(item),
                },
            )

    def upsert_archive(self, archive):
        self.upsert("shelf_archives", {"name": archive.get("name"), "raw": as_json(archive)}, ["name"])
        row = self.select_one("SELECT id FROM shelf_archives WHERE name=%s", [archive.get("name")])
        return row["id"]

    def upsert_book(self, book):
        if not book or not book.get("bookId"):
            return
        self.upsert(
            "books",
            {
                "book_id": book.get("bookId"),
                "title": book.get("title"),
                "author": book.get("author"),
                "translator": book.get("translator"),
                "cover": book.get("cover"),
                "publisher": book.get("publisher"),
                "intro": book.get("intro"),
                "category": book.get("category"),
                "isbn": book.get("isbn"),
                "format": book.get("format"),
                "version": first_present(book.get("version"), book.get("bookVersion")),
                "type": book.get("type"),
                "price": book.get("price"),
                "pay_type": book.get("payType"),
                "last_chapter_idx": book.get("lastChapterIdx"),
                "finished": book.get("finished"),
                "publish_time": first_present(book.get("publishTime")),
                "new_rating": book.get("newRating"),
                "new_rating_count": book.get("newRatingCount"),
                "extra": as_json(book),
            },
            ["book_id"],
        )
        for category in book.get("categories") or []:
            self.upsert_book_category(book.get("bookId"), category)

    def upsert_book_category(self, book_id, category):
        self.upsert(
            "book_categories",
            {
                "book_id": book_id,
                "category_id": category.get("categoryId"),
                "sub_category_id": category.get("subCategoryId"),
                "category_type": category.get("categoryType"),
                "title": category.get("title"),
                "raw": as_json(category),
            },
            ["book_id", "category_id", "sub_category_id", "category_type"],
        )

    def upsert_user(self, author):
        if not author or not author.get("userVid"):
            return None
        user_vid = author.get("userVid")
        self.upsert(
            "users",
            {
                "user_vid": user_vid,
                "name": author.get("name"),
                "avatar": author.get("avatar"),
                "is_following": as_bool(author.get("isFollowing")),
                "is_follower": as_bool(author.get("isFollower")),
                "is_deep_v": as_bool(author.get("isDeepV")),
                "deep_v_title": author.get("deepVTitle"),
                "medal_info": as_json(author.get("medalInfo")),
                "raw": as_json(author),
            },
            ["user_vid"],
        )
        return user_vid

    def upsert_review(self, review, source, likes_count=None, comments_count=None):
        review_id = review.get("reviewId")
        if not review_id:
            return
        book = review.get("book") or {}
        book_id = first_present(review.get("bookId"), book.get("bookId"))
        if book_id:
            book_payload = dict(book)
            book_payload.setdefault("bookId", book_id)
            self.upsert_book(book_payload)
        author_vid = self.upsert_user(review.get("author") or {})
        self.upsert(
            "reviews",
            {
                "review_id": review_id,
                "book_id": book_id,
                "author_user_vid": author_vid,
                "abstract_text": review.get("abstract"),
                "content": review.get("content"),
                "html_content": review.get("htmlContent"),
                "range_text": review.get("range"),
                "chapter_uid": review.get("chapterUid"),
                "chapter_idx": review.get("chapterIdx"),
                "chapter_name": review.get("chapterName"),
                "star": review.get("star"),
                "is_finish": review.get("isFinish"),
                "is_private": review.get("isPrivate"),
                "is_deep_v": as_bool(review.get("isDeepV")),
                "type": review.get("type"),
                "color_style": review.get("colorStyle"),
                "title": review.get("title"),
                "create_time": review.get("createTime"),
                "likes_count": likes_count,
                "comments_count": comments_count,
                "source": source,
                "pencil_note": as_json(review.get("pencilNote")),
                "raw": as_json(review),
            },
            ["review_id"],
        )

    def extract_book(self, obj):
        if not isinstance(obj, dict):
            return None
        if obj.get("bookId"):
            return obj
        for key in ("book", "bookInfo", "info"):
            nested = obj.get(key)
            if isinstance(nested, dict):
                found = self.extract_book(nested)
                if found:
                    return found
        return None

    def iter_book_like(self, obj):
        if isinstance(obj, dict):
            if obj.get("bookId"):
                yield obj
                return
            for value in obj.values():
                yield from self.iter_book_like(value)
        elif isinstance(obj, list):
            for value in obj:
                yield from self.iter_book_like(value)
