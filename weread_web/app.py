import os
import time
from calendar import monthrange
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from threading import RLock

import pymysql
from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent


def load_dotenv(path):
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / "weread_scrapy" / ".env")

CACHE_TTL_SECONDS = int(os.getenv("WEREAD_CACHE_TTL_SECONDS", "600"))
_cache = {}
_cache_lock = RLock()


def mysql_config():
    return {
        "host": os.getenv("WEREAD_MYSQL_HOST", "localhost"),
        "port": int(os.getenv("WEREAD_MYSQL_PORT", "3306")),
        "user": os.getenv("WEREAD_MYSQL_USER", "root"),
        "password": os.getenv("WEREAD_MYSQL_PASSWORD", "111111"),
        "database": os.getenv("WEREAD_MYSQL_DATABASE", "weread_api"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }


@contextmanager
def db_cursor():
    connection = pymysql.connect(**mysql_config())
    try:
        with connection.cursor() as cursor:
            yield cursor
    finally:
        connection.close()


def fetch_one(sql, params=None):
    with db_cursor() as cursor:
        cursor.execute(sql, params or ())
        return cursor.fetchone()


def fetch_all(sql, params=None):
    with db_cursor() as cursor:
        cursor.execute(sql, params or ())
        return cursor.fetchall()


def ok(data):
    return jsonify({"ok": True, "data": data})


def cached_ok(cache_key, loader, ttl_seconds=None):
    ttl = CACHE_TTL_SECONDS if ttl_seconds is None else ttl_seconds
    now = time.time()
    with _cache_lock:
        cached = _cache.get(cache_key)
        if cached and cached["expires_at"] > now:
            response = ok(cached["data"])
            response.headers["X-Weread-Cache"] = "HIT"
            response.headers["Cache-Control"] = f"private, max-age={max(0, int(cached['expires_at'] - now))}"
            return response

    data = loader()
    with _cache_lock:
        _cache[cache_key] = {"data": data, "expires_at": now + ttl}
    response = ok(data)
    response.headers["X-Weread-Cache"] = "MISS"
    response.headers["Cache-Control"] = f"private, max-age={ttl}"
    return response


def api_error(error, status=500):
    return jsonify({"ok": False, "error": str(error)}), status


app = Flask(__name__)

@app.get("/api/_version")
def api_version():
    # Also run the actual categories query directly for debugging
    rows = fetch_all(
        """
        SELECT COALESCE(NULLIF(SUBSTRING_INDEX(category, '-', 1), ''), '未分类') AS category, COUNT(*) AS count
        FROM books
        GROUP BY COALESCE(NULLIF(SUBSTRING_INDEX(category, '-', 1), ''), '未分类')
        ORDER BY count DESC, category ASC
        """
    )
    return ok({
        "sql_mode": "SUBSTRING_INDEX",
        "debug": False,
        "version": 4,
        "direct_query_count": len(rows),
        "direct_query_sample": rows[:5],
        "cache_key": "categories",
    })

app.jinja_env.variable_start_string = "[["
app.jinja_env.variable_end_string = "]]"


@app.get("/")
def index():
    response = app.make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.get("/api/summary")
def summary():
    try:
        def load_summary():
            counts = fetch_one(
                """
                SELECT
                  (SELECT COUNT(*) FROM books) AS books,
                  (SELECT COUNT(*) FROM shelf_books) AS shelf_books,
                  (SELECT COUNT(*) FROM reading_progress) AS reading_progress,
                  (SELECT COUNT(*) FROM user_bookmarks) AS bookmarks,
                  (SELECT COUNT(*) FROM reviews WHERE source = 'mine') AS reviews
                """
            )
            stats = fetch_one(
                """
                SELECT mode, base_time, read_days, total_read_time, day_average_read_time,
                       prefer_category_word, wr_read_time, wr_listen_time, fetched_at
                FROM reading_stats
                ORDER BY fetched_at DESC
                LIMIT 1
                """
            )
            progress_stats = fetch_one(
                """
                SELECT
                  COALESCE(SUM(reading_time), 0) AS total_read_time,
                  COUNT(CASE WHEN reading_time > 0 THEN 1 END) AS read_books,
                  COUNT(DISTINCT CASE
                    WHEN reading_time > 0 AND update_time IS NOT NULL AND update_time > 0
                    THEN DATE(FROM_UNIXTIME(update_time))
                  END) AS progress_update_days
                FROM reading_progress
                """
            )
            long_range_stats = fetch_one(
                """
                SELECT mode, read_days
                FROM reading_stats
                WHERE mode IN ('overall', 'annually') AND read_days IS NOT NULL AND read_days > 0
                ORDER BY FIELD(mode, 'overall', 'annually'), fetched_at DESC
                LIMIT 1
                """
            )
            recorded_days = fetch_one(
                """
                SELECT COUNT(*) AS read_days
                FROM reading_stat_daily_times
                WHERE read_time > 0
                """
            )
            progress_span = fetch_one(
                """
                SELECT
                  MIN(update_time) AS min_update_time,
                  MAX(update_time) AS max_update_time
                FROM reading_progress
                WHERE update_time IS NOT NULL AND update_time > 0
                """
            )
            all_total = int((progress_stats or {}).get("total_read_time") or 0)

            reg_time = None
            if stats and stats.get("regist_time"):
                reg_time = stats["regist_time"]
            else:
                reg_row = fetch_one("SELECT regist_time FROM reading_stats WHERE regist_time IS NOT NULL ORDER BY fetched_at DESC LIMIT 1")
                if reg_row:
                    reg_time = reg_row["regist_time"]
           
            # Find current user from their reviews
            profile_row = fetch_one(
                """
                SELECT u.name, u.avatar
                FROM users u
                JOIN reviews r ON r.author_user_vid = u.user_vid
                WHERE r.source = 'mine' AND u.name IS NOT NULL
                ORDER BY r.create_time DESC
                LIMIT 1
                """
            )
            profile_name = os.getenv("WEREAD_USER_NAME", None)
            profile_avatar = os.getenv("WEREAD_USER_AVATAR", None)
            if profile_row:
                profile_name = profile_name or profile_row.get("name")
                profile_avatar = profile_avatar or profile_row.get("avatar")
            profile_name = profile_name or "微信读书用户"

            if reg_time:
                all_read_days = (datetime.now().date() - datetime.fromtimestamp(reg_time).date()).days
                read_days_source = "membership_days"
            elif (recorded_days or {}).get("read_days"):
                all_read_days = int(recorded_days["read_days"])
                read_days_source = "recorded_daily_times"
            elif (long_range_stats or {}).get("read_days"):
                all_read_days = int(long_range_stats["read_days"])
                read_days_source = long_range_stats["mode"]
            elif (progress_stats or {}).get("progress_update_days"):
                all_read_days = int(progress_stats["progress_update_days"])
                read_days_source = "reading_progress_active_days"
            elif (progress_span or {}).get("min_update_time") and (progress_span or {}).get("max_update_time"):
                start_day = datetime.fromtimestamp(progress_span["min_update_time"]).date()
                end_day = datetime.fromtimestamp(progress_span["max_update_time"]).date()
                all_read_days = max(1, (end_day - start_day).days + 1)
                read_days_source = "reading_progress_span"
            else:
                all_read_days = 0
                read_days_source = "none"
            all_time_stats = {
                "total_read_time": all_total,
                "read_days": all_read_days,
                "day_average_read_time": int(all_total / all_read_days) if all_read_days else 0,
                "read_books": (progress_stats or {}).get("read_books") or 0,
                "read_days_source": read_days_source,
            }
            latest = fetch_one("SELECT MAX(fetched_at) AS latest_sync FROM api_responses")
            return {
                "counts": counts,
                "latest_stats": stats,
                "all_time_stats": all_time_stats,
                "latest_sync": latest["latest_sync"] if latest else None,
                "user": {
                    "name": profile_name,
                    "avatar": profile_avatar or "",
                    "membership_days": (datetime.now().date() - datetime.fromtimestamp(reg_time).date()).days if reg_time else None,
                    "regist_time": reg_time,
                }
            }

        return cached_ok("summary", load_summary)
    except Exception as exc:
        return api_error(exc)


@app.post("/api/cache/clear")
def clear_cache():
    with _cache_lock:
        _cache.clear()
    return ok({"cleared": True})


@app.get("/api/cache/status")
def cache_status():
    now = time.time()
    with _cache_lock:
        entries = [
            {"key": key, "ttl_seconds": max(0, int(value["expires_at"] - now))}
            for key, value in sorted(_cache.items())
        ]
    return ok({"ttl_seconds": CACHE_TTL_SECONDS, "entries": entries})


@app.get("/api/books")
def books():
    try:
        q = (request.args.get("q") or "").strip()
        sort = request.args.get("sort", "updated")
        limit = min(max(int(request.args.get("limit", 40)), 1), 5000)
        offset = max(int(request.args.get("offset", 0)), 0)

        where = ""
        params = []
        if q:
            where = "WHERE b.title LIKE %s OR b.author LIKE %s OR b.category LIKE %s"
            needle = f"%{q}%"
            params.extend([needle, needle, needle])

        order_map = {
            "title": "b.title IS NULL, b.title ASC",
            "rating": "b.new_rating DESC, b.title ASC",
            "progress": "rp.progress DESC, b.title ASC",
            "updated": "COALESCE(rp.update_time, sb.read_update_time, sb.update_time, 0) DESC, b.title ASC",
        }
        order_by = order_map.get(sort, order_map["updated"])

        total = fetch_one(f"SELECT COUNT(*) AS total FROM books b {where}", params)["total"]
        rows = fetch_all(
            f"""
            SELECT b.book_id, b.title, b.author, b.cover, b.category, b.publisher,
                   b.new_rating, b.new_rating_count, b.publish_time,
                   rp.progress, rp.reading_time, rp.update_time AS progress_update_time,
                   rp.summary AS progress_summary,
                   sb.finish_reading, sb.read_update_time
            FROM books b
            LEFT JOIN reading_progress rp ON rp.book_id = b.book_id
            LEFT JOIN shelf_books sb ON sb.book_id = b.book_id
            {where}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
            """,
            params + [limit, offset],
        )
        return ok({"items": rows, "total": total, "limit": limit, "offset": offset})
    except Exception as exc:
        return api_error(exc)


@app.get("/api/books/<book_id>")
def book_detail(book_id):
    try:
        book = fetch_one(
            """
           SELECT b.*, rp.progress, rp.reading_time, rp.chapter_idx, rp.chapter_offset,
                  rp.update_time AS progress_update_time, rp.summary AS progress_summary,
                  sb.finish_reading, sb.secret, sb.read_update_time,
                  brd.good, brd.fair, brd.poor, brd.recent, brd.deep_v, brd.my_rating, brd.rating_title,
                  (SELECT COALESCE(SUM(word_count), 0) FROM chapters WHERE book_id = b.book_id) AS total_words
            FROM books b
            LEFT JOIN reading_progress rp ON rp.book_id = b.book_id
            LEFT JOIN shelf_books sb ON sb.book_id = b.book_id
            LEFT JOIN book_rating_details brd ON brd.book_id = b.book_id
            WHERE b.book_id = %s
            """,
            [book_id],
        )
        if not book:
            return api_error("Book not found", 404)

        bookmarks = fetch_all(
            """
            SELECT bookmark_id, chapter_uid, chapter_idx, range_text, mark_text,
                   color_style, type, create_time
            FROM user_bookmarks
            WHERE book_id = %s
            ORDER BY create_time DESC
            LIMIT 20
            """,
            [book_id],
        )
        reviews = fetch_all(
            """
            SELECT review_id, abstract_text, content, html_content, chapter_name,
                   range_text, type, create_time, is_private
            FROM reviews
            WHERE book_id = %s AND type = 1 AND source = 'mine'
            ORDER BY create_time DESC
            LIMIT 20
            """,
            [book_id],
        )

        return ok({"book": book, "bookmarks": bookmarks, "reviews": reviews})
    except Exception as exc:
        return api_error(exc)


@app.get("/api/categories")
def categories():
    try:
        def load_categories():
            return fetch_all(
                                """
                SELECT category, COUNT(*) AS count,
                  (SELECT b2.book_id FROM books b2
                   LEFT JOIN reading_progress rp2 ON rp2.book_id = b2.book_id
                   WHERE COALESCE(NULLIF(SUBSTRING_INDEX(b2.category, '-', 1), ''), '未分类') = cat.category
                   ORDER BY COALESCE(rp2.reading_time, 0) DESC, b2.title ASC LIMIT 1) AS rep_book_id,
                  (SELECT b2.title FROM books b2
                   LEFT JOIN reading_progress rp2 ON rp2.book_id = b2.book_id
                   WHERE COALESCE(NULLIF(SUBSTRING_INDEX(b2.category, '-', 1), ''), '未分类') = cat.category
                   ORDER BY COALESCE(rp2.reading_time, 0) DESC, b2.title ASC LIMIT 1) AS rep_title,
                  (SELECT b2.cover FROM books b2
                   LEFT JOIN reading_progress rp2 ON rp2.book_id = b2.book_id
                   WHERE COALESCE(NULLIF(SUBSTRING_INDEX(b2.category, '-', 1), ''), '未分类') = cat.category
                   ORDER BY COALESCE(rp2.reading_time, 0) DESC, b2.title ASC LIMIT 1) AS rep_cover,
                  (SELECT b2.author FROM books b2
                   LEFT JOIN reading_progress rp2 ON rp2.book_id = b2.book_id
                   WHERE COALESCE(NULLIF(SUBSTRING_INDEX(b2.category, '-', 1), ''), '未分类') = cat.category
                   ORDER BY COALESCE(rp2.reading_time, 0) DESC, b2.title ASC LIMIT 1) AS rep_author,
                  (SELECT b2.new_rating FROM books b2
                   LEFT JOIN reading_progress rp2 ON rp2.book_id = b2.book_id
                   WHERE COALESCE(NULLIF(SUBSTRING_INDEX(b2.category, '-', 1), ''), '未分类') = cat.category
                   ORDER BY COALESCE(rp2.reading_time, 0) DESC, b2.title ASC LIMIT 1) AS rep_rating
                FROM (
                  SELECT COALESCE(NULLIF(SUBSTRING_INDEX(b.category, '-', 1), ''), '未分类') AS category
                  FROM books b
                ) cat
                GROUP BY cat.category
                ORDER BY count DESC, cat.category ASC
                """
            )

        return cached_ok("categories", load_categories)
    except Exception as exc:
        return api_error(exc)


@app.get("/api/recent-notes")
def recent_notes():
    try:
        def load_recent_notes():
           return fetch_all(
               """
               SELECT r.review_id AS id, r.book_id, b.title AS book_title, b.author,
                      b.cover, b.category, b.publisher, b.new_rating,
                      rp.progress, rp.reading_time,
                      r.abstract_text, r.content, r.chapter_name, r.create_time,
                      'note' AS type, r.is_private
               FROM reviews r
               LEFT JOIN books b ON b.book_id = r.book_id
               LEFT JOIN reading_progress rp ON rp.book_id = r.book_id
               WHERE r.source = 'mine'
                 AND r.content IS NOT NULL AND TRIM(r.content) <> ''
               UNION ALL
               SELECT ub.bookmark_id AS id, ub.book_id, b.title AS book_title, b.author,
                      b.cover, b.category, b.publisher, b.new_rating,
                      rp.progress, rp.reading_time,
                      NULL AS abstract_text, ub.mark_text AS content, NULL AS chapter_name,
                      ub.create_time,
                      'bookmark' AS type, NULL AS is_private
               FROM user_bookmarks ub
               LEFT JOIN books b ON b.book_id = ub.book_id
               LEFT JOIN reading_progress rp ON rp.book_id = ub.book_id
               ORDER BY create_time DESC
               LIMIT 20
               """
            )

        return cached_ok("thought-notes:mine", load_recent_notes)
    except Exception as exc:
        return api_error(exc)


@app.get("/api/currently-reading")
def currently_reading():
    try:
        def load_currently_reading():
            return fetch_all(
                """
                SELECT b.book_id, b.title, b.author, b.cover, b.category,
                       rp.progress, rp.reading_time, rp.update_time, rp.summary
                FROM reading_progress rp
                JOIN books b ON b.book_id = rp.book_id
                WHERE rp.progress > 0 AND rp.progress < 100
                ORDER BY rp.update_time DESC
                LIMIT 4
                """
            )

        return cached_ok("currently-reading", load_currently_reading)
    except Exception as exc:
        return api_error(exc)


@app.get("/api/highlights")
def highlights():
    try:
        mode = request.args.get("mode", "random")

        def load_highlights():
            order_by = "RAND()" if mode == "random" else "ub.create_time DESC"
            return fetch_all(
                f"""
                SELECT ub.bookmark_id, ub.book_id, ub.mark_text, ub.chapter_idx,
                       ub.range_text, ub.create_time, b.title AS book_title, b.author
                FROM user_bookmarks ub
                LEFT JOIN books b ON b.book_id = ub.book_id
                WHERE ub.mark_text IS NOT NULL AND ub.mark_text <> ''
                ORDER BY {order_by}
                LIMIT 12
                """
            )

        return cached_ok(f"highlights:{mode}", load_highlights, ttl_seconds=300)
    except Exception as exc:
        return api_error(exc)


@app.get("/api/reading-heatmap")
def reading_heatmap():
    try:
        def load_heatmap():
            rows = fetch_all(
                """
                SELECT
                  DATE(FROM_UNIXTIME(dt.day_timestamp)) AS read_date,
                  MAX(dt.read_time) AS read_time
                FROM reading_stat_daily_times dt
                JOIN reading_stats rs ON rs.id = dt.reading_stat_id
                WHERE rs.mode IN ('monthly', 'annually', 'overall')
                  AND dt.read_time BETWEEN 0 AND 86400
                GROUP BY DATE(FROM_UNIXTIME(dt.day_timestamp))
                ORDER BY read_date ASC
                """
            )
            read_by_date = {
                row["read_date"]: int(row["read_time"] or 0)
                for row in rows
                if row.get("read_date") is not None
            }

            available_years = sorted({read_date.year for read_date in read_by_date}, reverse=True)
            if available_years:
                requested_year = request.args.get("year", type=int)
                year = requested_year if requested_year in available_years else available_years[0]
            else:
                year = datetime.now().year

            months = []
            data_dates_by_month = {}
            for read_date in read_by_date:
                data_dates_by_month.setdefault((read_date.year, read_date.month), []).append(read_date)
            year_read_times = [
                read_time
                for read_date, read_time in read_by_date.items()
                if read_date.year == year
            ]
            max_read_time = max(year_read_times or [0])

            for month in range(1, 13):
                _, last_day = monthrange(year, month)
                month_start = datetime(year, month, 1).date()
                month_end = datetime(year, month, last_day).date()
                month_data_dates = data_dates_by_month.get((year, month), [])
                if month_data_dates:
                    month_end = max(month_data_dates)
                elif year == datetime.now().year and month > datetime.now().month:
                    month_end = month_start - timedelta(days=1)

                days = []
                current = month_start
                while current <= month_end:
                    read_time = read_by_date.get(current, 0)
                    if max_read_time <= 0 or read_time <= 0:
                        level = 0
                    else:
                        level = min(4, max(1, int((read_time / max_read_time) * 4 + 0.999)))
                    days.append(
                        {
                            "date": current.isoformat(),
                            "timestamp": int(datetime(current.year, current.month, current.day).timestamp()),
                            "read_time": read_time,
                            "level": level,
                            "weekday": current.weekday(),
                        }
                    )
                    current += timedelta(days=1)

                month_total = sum(day["read_time"] for day in days)
                month_active_days = sum(1 for day in days if day["read_time"] > 0)
                months.append(
                    {
                        "key": f"{year}-{month:02d}",
                        "label": f"{month}月",
                        "year": year,
                        "month": month,
                        "start_date": month_start.isoformat(),
                        "end_date": month_end.isoformat(),
                        "days": days,
                        "active_days": month_active_days,
                        "total_read_time": month_total,
                        "max_read_time": max((day["read_time"] for day in days), default=0),
                    }
                )

            active_months = [month for month in months if month["active_days"] > 0]
            today = datetime.now().date()
            default_month = f"{today.year}-{today.month:02d}" if year == today.year else (
                active_months[-1]["key"] if active_months else months[0]["key"]
            )
            if not any(month["key"] == default_month for month in months):
                default_month = active_months[-1]["key"] if active_months else months[0]["key"]

            return {
                "year": year,
                "years": available_years,
                "default_month": default_month,
                "max_read_time": max_read_time,
                "active_days": sum(month["active_days"] for month in months),
                "total_read_time": sum(month["total_read_time"] for month in months),
                "months": months,
            }

        return cached_ok(f"reading-heatmap:{request.args.get('year') or 'latest'}", load_heatmap)
    except Exception as exc:
        return api_error(exc)


@app.get("/api/persona")
def persona():
    try:
        def load_persona():
            counts = fetch_one(
                """
                SELECT
                  (SELECT COUNT(*) FROM books) AS books,
                  (SELECT COUNT(*) FROM user_bookmarks) AS bookmarks,
                  (SELECT COUNT(*) FROM reviews WHERE source = 'mine') AS reviews,
                  (SELECT COUNT(*) FROM reading_progress WHERE progress > 0 AND progress < 100) AS in_progress,
                  (SELECT COUNT(*) FROM reading_progress WHERE progress >= 100) AS completed,
                  (SELECT ROUND(AVG(progress), 1) FROM reading_progress) AS avg_progress
                """
            )
            top_category = fetch_one(
                """
                SELECT COALESCE(NULLIF(category, ''), '未分类') AS category, COUNT(*) AS count
                FROM books
                GROUP BY COALESCE(NULLIF(category, ''), '未分类')
                ORDER BY count DESC
                LIMIT 1
                """
            )
            longest = fetch_one(
                """
                SELECT b.title, b.author, rp.reading_time
                FROM reading_progress rp
                JOIN books b ON b.book_id = rp.book_id
                WHERE rp.reading_time IS NOT NULL
                ORDER BY rp.reading_time DESC
                LIMIT 1
                """
            )

            book_count = counts["books"] or 0
            bookmarks = counts["bookmarks"] or 0
            reviews = counts["reviews"] or 0
            in_progress = counts["in_progress"] or 0
            completed = counts["completed"] or 0
            note_density = round((bookmarks + reviews) / book_count, 2) if book_count else 0
            category = (top_category or {}).get("category") or "未分类"

            tags = []
            if book_count >= 1000:
                tags.append({"name": "千本藏书家", "reason": f"书架里已经有 {book_count} 本书"})
            if "历史" in category:
                tags.append({"name": "历史纵深派", "reason": f"最多的分类是「{category}」"})
            elif "计算机" in category or "科技" in category:
                tags.append({"name": "技术探索者", "reason": f"最多的分类是「{category}」"})
            else:
                tags.append({"name": "主题型读者", "reason": f"最多的分类是「{category}」"})
            if bookmarks >= 100:
                tags.append({"name": "划线型学习者", "reason": f"累计保存 {bookmarks} 条个人划线"})
            if reviews >= 100:
                tags.append({"name": "笔记型读者", "reason": f"累计留下 {reviews} 条笔记和想法"})
            if in_progress >= 30:
                tags.append({"name": "多线并读者", "reason": f"有 {in_progress} 本书处于阅读中"})
            if completed >= 50:
                tags.append({"name": "完成度稳健", "reason": f"已读完 {completed} 本书"})

            headline = tags[0]["name"] if tags else "安静读者"
            summary = f"你是一位{headline}，偏爱「{category}」，当前有 {in_progress} 本书在读。"
            return {
                "headline": headline,
                "summary": summary,
                "tags": tags[:5],
                "top_category": top_category,
                "longest_read": longest,
                "note_density": note_density,
                "avg_progress": counts["avg_progress"],
            }

        return cached_ok("persona", load_persona)
    except Exception as exc:
        return api_error(exc)


@app.get("/api/summary-uncached")
def summary_uncached():
    try:
        counts = fetch_one(
            """
            SELECT
              (SELECT COUNT(*) FROM books) AS books,
              (SELECT COUNT(*) FROM shelf_books) AS shelf_books,
              (SELECT COUNT(*) FROM reading_progress) AS reading_progress,
              (SELECT COUNT(*) FROM user_bookmarks) AS bookmarks,
              (SELECT COUNT(*) FROM reviews WHERE source = 'mine') AS reviews
            """
        )
        stats = fetch_one(
            """
            SELECT mode, base_time, read_days, total_read_time, day_average_read_time,
                   prefer_category_word, wr_read_time, wr_listen_time, fetched_at
            FROM reading_stats
            ORDER BY fetched_at DESC
            LIMIT 1
            """
        )
        progress_stats = fetch_one(
            """
            SELECT
              COALESCE(SUM(reading_time), 0) AS total_read_time,
              COUNT(CASE WHEN reading_time > 0 THEN 1 END) AS read_books,
              COUNT(DISTINCT CASE
                WHEN reading_time > 0 AND update_time IS NOT NULL AND update_time > 0
                THEN DATE(FROM_UNIXTIME(update_time))
              END) AS progress_update_days
            FROM reading_progress
            """
        )
        long_range_stats = fetch_one(
            """
            SELECT mode, read_days
            FROM reading_stats
            WHERE mode IN ('overall', 'annually') AND read_days IS NOT NULL AND read_days > 0
            ORDER BY FIELD(mode, 'overall', 'annually'), fetched_at DESC
            LIMIT 1
            """
        )
        recorded_days = fetch_one(
            """
            SELECT COUNT(*) AS read_days
            FROM reading_stat_daily_times
            WHERE read_time > 0
            """
        )
        progress_span = fetch_one(
            """
            SELECT
              MIN(update_time) AS min_update_time,
              MAX(update_time) AS max_update_time
            FROM reading_progress
            WHERE update_time IS NOT NULL AND update_time > 0
            """
        )
        all_total = int((progress_stats or {}).get("total_read_time") or 0)

        reg_time = None
        if stats and stats.get("regist_time"):
            reg_time = stats["regist_time"]
        else:
            reg_row = fetch_one("SELECT regist_time FROM reading_stats WHERE regist_time IS NOT NULL ORDER BY fetched_at DESC LIMIT 1")
            if reg_row:
                reg_time = reg_row["regist_time"]
        if reg_time:
            all_read_days = (datetime.now().date() - datetime.fromtimestamp(reg_time).date()).days
            read_days_source = "membership_days"
        elif (recorded_days or {}).get("read_days"):
            all_read_days = int(recorded_days["read_days"])
            read_days_source = "recorded_daily_times"
        elif (long_range_stats or {}).get("read_days"):
            all_read_days = int(long_range_stats["read_days"])
            read_days_source = long_range_stats["mode"]
        elif (progress_stats or {}).get("progress_update_days"):
            all_read_days = int(progress_stats["progress_update_days"])
            read_days_source = "reading_progress_active_days"
        elif (progress_span or {}).get("min_update_time") and (progress_span or {}).get("max_update_time"):
            start_day = datetime.fromtimestamp(progress_span["min_update_time"]).date()
            end_day = datetime.fromtimestamp(progress_span["max_update_time"]).date()
            all_read_days = max(1, (end_day - start_day).days + 1)
            read_days_source = "reading_progress_span"
        else:
            all_read_days = 0
            read_days_source = "none"
            all_time_stats = {
            "total_read_time": all_total,
            "read_days": all_read_days,
            "day_average_read_time": int(all_total / all_read_days) if all_read_days else 0,
            "read_books": (progress_stats or {}).get("read_books") or 0,
            "read_days_source": read_days_source,
        }
        latest = fetch_one("SELECT MAX(fetched_at) AS latest_sync FROM api_responses")
        return ok({
            "counts": counts,
            "latest_stats": stats,
            "all_time_stats": all_time_stats,
            "latest_sync": latest["latest_sync"] if latest else None,
        })
    except Exception as exc:
        return api_error(exc)



@app.get("/api/books/light")
def books_light():
    """Lightweight endpoint for BubbleMap — only book_id, title, author, cover."""
    try:
        limit = min(max(int(request.args.get("limit", 2000)), 1), 5000)
        offset = max(int(request.args.get("offset", 0)), 0)
        rows = fetch_all(
            """
            SELECT book_id, title, author, cover
            FROM books
            WHERE cover IS NOT NULL AND cover != ''
              AND title IS NOT NULL AND title != ''
              AND author IS NOT NULL AND author != ''
            ORDER BY book_id
            LIMIT %s OFFSET %s
            """,
            [limit, offset],
        )
        total = fetch_one("SELECT COUNT(*) AS total FROM books WHERE cover IS NOT NULL AND cover != '' AND title IS NOT NULL AND title != ''")["total"]
        return ok({"items": rows, "total": total, "limit": limit, "offset": offset})
    except Exception as exc:
        return api_error(exc)



if __name__ == "__main__":
    app.run(host=os.getenv("WEREAD_WEB_HOST", "0.0.0.0"), port=int(os.getenv("WEREAD_WEB_PORT", "5050")), debug=False)
