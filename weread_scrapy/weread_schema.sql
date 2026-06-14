CREATE DATABASE IF NOT EXISTS weread_api
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE weread_api;

CREATE TABLE IF NOT EXISTS api_responses (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  api_name VARCHAR(128) NOT NULL,
  request_params JSON NULL,
  response_body JSON NOT NULL,
  fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_api_responses_api_time (api_name, fetched_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS books (
  book_id VARCHAR(64) NOT NULL,
  title VARCHAR(512) NULL,
  author VARCHAR(512) NULL,
  translator VARCHAR(512) NULL,
  cover VARCHAR(2048) NULL,
  publisher VARCHAR(512) NULL,
  intro MEDIUMTEXT NULL,
  category VARCHAR(255) NULL,
  isbn VARCHAR(64) NULL,
  format VARCHAR(64) NULL,
  version BIGINT NULL,
  type INT NULL,
  price DECIMAL(10,2) NULL,
  pay_type INT NULL,
  last_chapter_idx INT NULL,
  finished TINYINT NULL,
  publish_time DATETIME NULL,
  new_rating INT NULL,
  new_rating_count INT NULL,
  extra JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id),
  KEY idx_books_title (title),
  KEY idx_books_author (author),
  KEY idx_books_category (category),
  KEY idx_books_isbn (isbn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS book_rating_details (
  book_id VARCHAR(64) NOT NULL,
  good INT NULL,
  fair INT NULL,
  poor INT NULL,
  recent INT NULL,
  deep_v INT NULL,
  my_rating VARCHAR(64) NULL,
  rating_title VARCHAR(255) NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id),
  CONSTRAINT fk_book_rating_details_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS book_categories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  book_id VARCHAR(64) NOT NULL,
  category_id BIGINT NULL,
  sub_category_id BIGINT NULL,
  category_type INT NULL,
  title VARCHAR(255) NULL,
  raw JSON NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_book_categories_book_category (book_id, category_id, sub_category_id, category_type),
  CONSTRAINT fk_book_categories_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chapter_syncs (
  book_id VARCHAR(64) NOT NULL,
  synckey BIGINT NULL,
  chapter_update_time BIGINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id),
  CONSTRAINT fk_chapter_syncs_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chapters (
  book_id VARCHAR(64) NOT NULL,
  chapter_uid BIGINT NOT NULL,
  chapter_idx INT NULL,
  level INT NULL,
  title VARCHAR(1024) NULL,
  word_count INT NULL,
  price INT NULL,
  paid TINYINT NULL,
  is_mp_chapter TINYINT NULL,
  update_time BIGINT NULL,
  raw JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id, chapter_uid),
  KEY idx_chapters_book_idx (book_id, chapter_idx),
  CONSTRAINT fk_chapters_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chapter_anchors (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  book_id VARCHAR(64) NOT NULL,
  chapter_uid BIGINT NOT NULL,
  anchor VARCHAR(255) NULL,
  title VARCHAR(1024) NULL,
  level INT NULL,
  raw JSON NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_chapter_anchors_anchor (book_id, chapter_uid, anchor),
  CONSTRAINT fk_chapter_anchors_chapter
    FOREIGN KEY (book_id, chapter_uid) REFERENCES chapters (book_id, chapter_uid)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reading_progress (
  book_id VARCHAR(64) NOT NULL,
  app_id VARCHAR(128) NULL,
  book_version BIGINT NULL,
  review_id VARCHAR(128) NULL,
  chapter_uid BIGINT NULL,
  chapter_idx INT NULL,
  chapter_offset INT NULL,
  progress INT NULL,
  reading_time INT NULL,
  start_reading_time BIGINT NULL,
  update_time BIGINT NULL,
  synckey BIGINT NULL,
  summary TEXT NULL,
  repair_offset_time BIGINT NULL,
  is_start_reading TINYINT NULL,
  tts_time INT NULL,
  install_id VARCHAR(128) NULL,
  record_reading_time INT NULL,
  response_timestamp BIGINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id),
  KEY idx_reading_progress_update_time (update_time),
  CONSTRAINT fk_reading_progress_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS search_sessions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  sid VARCHAR(128) NULL,
  keyword VARCHAR(255) NOT NULL,
  scope INT NULL,
  max_idx INT NULL,
  count_requested INT NULL,
  has_more TINYINT NULL,
  raw JSON NULL,
  searched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_search_sessions_keyword (keyword),
  KEY idx_search_sessions_sid (sid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS search_results (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  search_session_id BIGINT UNSIGNED NOT NULL,
  result_idx INT NULL,
  result_type VARCHAR(64) NULL,
  book_id VARCHAR(64) NULL,
  title VARCHAR(512) NULL,
  author VARCHAR(512) NULL,
  raw JSON NOT NULL,
  PRIMARY KEY (id),
  KEY idx_search_results_book (book_id),
  CONSTRAINT fk_search_results_session
    FOREIGN KEY (search_session_id) REFERENCES search_sessions (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS book_recommendations (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  source VARCHAR(32) NOT NULL,
  source_book_id VARCHAR(64) NULL,
  session_id VARCHAR(128) NULL,
  max_idx INT NULL,
  book_id VARCHAR(64) NOT NULL,
  rank_no INT NULL,
  title VARCHAR(512) NULL,
  author VARCHAR(512) NULL,
  category VARCHAR(255) NULL,
  cover VARCHAR(2048) NULL,
  intro MEDIUMTEXT NULL,
  price DECIMAL(10,2) NULL,
  pay_type INT NULL,
  type INT NULL,
  raw JSON NULL,
  fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_book_recommendations_source (source, source_book_id),
  KEY idx_book_recommendations_book (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS shelf_books (
  book_id VARCHAR(64) NOT NULL,
  finish_reading TINYINT NULL,
  read_update_time BIGINT NULL,
  secret TINYINT NULL,
  update_time BIGINT NULL,
  is_top TINYINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id),
  CONSTRAINT fk_shelf_books_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS shelf_archives (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_shelf_archives_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS shelf_archive_books (
  archive_id BIGINT UNSIGNED NOT NULL,
  book_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (archive_id, book_id),
  KEY idx_shelf_archive_books_book (book_id),
  CONSTRAINT fk_shelf_archive_books_archive
    FOREIGN KEY (archive_id) REFERENCES shelf_archives (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS shelf_archive_albums (
  archive_id BIGINT UNSIGNED NOT NULL,
  album_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (archive_id, album_id),
  CONSTRAINT fk_shelf_archive_albums_archive
    FOREIGN KEY (archive_id) REFERENCES shelf_archives (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS albums (
  album_id VARCHAR(64) NOT NULL,
  name VARCHAR(512) NULL,
  author_name VARCHAR(512) NULL,
  cover VARCHAR(2048) NULL,
  intro MEDIUMTEXT NULL,
  update_time BIGINT NULL,
  finish_status VARCHAR(128) NULL,
  type INT NULL,
  track_count INT NULL,
  secret TINYINT NULL,
  lecture_paid TINYINT NULL,
  lecture_read_update_time BIGINT NULL,
  is_top TINYINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (album_id),
  KEY idx_albums_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS mp_collection (
  book_id VARCHAR(64) NOT NULL,
  show_flag TINYINT NULL,
  title VARCHAR(512) NULL,
  cover VARCHAR(2048) NULL,
  secret TINYINT NULL,
  pay_type INT NULL,
  paid TINYINT NULL,
  update_time BIGINT NULL,
  read_update_time BIGINT NULL,
  is_top TINYINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notebook_syncs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  synckey BIGINT NULL,
  total_book_count INT NULL,
  total_note_count INT NULL,
  no_book_review_count INT NULL,
  has_more TINYINT NULL,
  last_sort BIGINT NULL,
  raw JSON NULL,
  fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_notebook_syncs_synckey (synckey)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notebooks (
  book_id VARCHAR(64) NOT NULL,
  notebook_sync_id BIGINT UNSIGNED NULL,
  review_count INT NULL,
  marked_status INT NULL,
  reading_progress INT NULL,
  note_count INT NULL,
  bookmark_count INT NULL,
  sort_value BIGINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (book_id),
  KEY idx_notebooks_sort (sort_value),
  CONSTRAINT fk_notebooks_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_notebooks_sync
    FOREIGN KEY (notebook_sync_id) REFERENCES notebook_syncs (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_bookmarks (
  bookmark_id VARCHAR(191) NOT NULL,
  book_id VARCHAR(64) NOT NULL,
  chapter_uid BIGINT NULL,
  chapter_idx INT NULL,
  range_text VARCHAR(128) NULL,
  mark_text MEDIUMTEXT NULL,
  color_style INT NULL,
  type INT NULL,
  create_time BIGINT NULL,
  raw JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (bookmark_id),
  KEY idx_user_bookmarks_book_chapter (book_id, chapter_uid),
  KEY idx_user_bookmarks_create_time (create_time),
  CONSTRAINT fk_user_bookmarks_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS bookmark_chapters (
  book_id VARCHAR(64) NOT NULL,
  chapter_uid BIGINT NOT NULL,
  chapter_idx INT NULL,
  title VARCHAR(1024) NULL,
  raw JSON NULL,
  PRIMARY KEY (book_id, chapter_uid),
  CONSTRAINT fk_bookmark_chapters_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS best_bookmarks (
  bookmark_id VARCHAR(191) NOT NULL,
  book_id VARCHAR(64) NOT NULL,
  user_vid BIGINT NULL,
  chapter_uid BIGINT NULL,
  range_text VARCHAR(128) NULL,
  simplified_range VARCHAR(128) NULL,
  traditional_range VARCHAR(128) NULL,
  mark_text MEDIUMTEXT NULL,
  total_count INT NULL,
  synckey BIGINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (bookmark_id),
  KEY idx_best_bookmarks_book_chapter (book_id, chapter_uid),
  KEY idx_best_bookmarks_total_count (total_count),
  CONSTRAINT fk_best_bookmarks_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS underline_stats (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  book_id VARCHAR(64) NOT NULL,
  chapter_uid BIGINT NOT NULL,
  range_text VARCHAR(128) NOT NULL,
  count_value INT NULL,
  score DOUBLE NULL,
  type INT NULL,
  synckey BIGINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_underline_stats_range (book_id, chapter_uid, range_text),
  KEY idx_underline_stats_hot (book_id, chapter_uid, count_value),
  CONSTRAINT fk_underline_stats_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
  user_vid BIGINT NOT NULL,
  name VARCHAR(255) NULL,
  avatar VARCHAR(2048) NULL,
  is_following TINYINT NULL,
  is_follower TINYINT NULL,
  is_deep_v TINYINT NULL,
  deep_v_title VARCHAR(255) NULL,
  medal_info JSON NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_vid),
  KEY idx_users_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reviews (
  review_id VARCHAR(191) NOT NULL,
  book_id VARCHAR(64) NULL,
  author_user_vid BIGINT NULL,
  abstract_text MEDIUMTEXT NULL,
  content MEDIUMTEXT NULL,
  html_content MEDIUMTEXT NULL,
  range_text VARCHAR(128) NULL,
  chapter_uid BIGINT NULL,
  chapter_idx INT NULL,
  chapter_name VARCHAR(1024) NULL,
  star INT NULL,
  is_finish TINYINT NULL,
  is_private TINYINT NULL,
  is_deep_v TINYINT NULL,
  type INT NULL,
  color_style INT NULL,
  title VARCHAR(512) NULL,
  create_time BIGINT NULL,
  likes_count INT NULL,
  comments_count INT NULL,
  source VARCHAR(64) NULL,
  pencil_note JSON NULL,
  raw JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (review_id),
  KEY idx_reviews_book (book_id),
  KEY idx_reviews_author (author_user_vid),
  KEY idx_reviews_create_time (create_time),
  KEY idx_reviews_chapter_range (book_id, chapter_uid, range_text),
  CONSTRAINT fk_reviews_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_reviews_user
    FOREIGN KEY (author_user_vid) REFERENCES users (user_vid)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS review_list_batches (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  book_id VARCHAR(64) NOT NULL,
  review_list_type INT NULL,
  synckey BIGINT NULL,
  max_idx INT NULL,
  count_requested INT NULL,
  reviews_has_more TINYINT NULL,
  reviews_has_5_star TINYINT NULL,
  reviews_has_1_star TINYINT NULL,
  reviews_has_recent TINYINT NULL,
  reviews_cnt INT NULL,
  recent_total_cnt INT NULL,
  friend_comment_count INT NULL,
  friend_unique_count INT NULL,
  deep_v_recommend_info JSON NULL,
  deep_v_recommend_value INT NULL,
  deep_v_unique_count INT NULL,
  raw JSON NULL,
  fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_review_list_batches_book (book_id),
  CONSTRAINT fk_review_list_batches_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS personal_review_batches (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  book_id VARCHAR(64) NOT NULL,
  synckey BIGINT NULL,
  total_count INT NULL,
  has_more TINYINT NULL,
  removed JSON NULL,
  raw JSON NULL,
  fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_personal_review_batches_book (book_id),
  CONSTRAINT fk_personal_review_batches_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS review_single_details (
  review_id VARCHAR(191) NOT NULL,
  synckey BIGINT NULL,
  html_content MEDIUMTEXT NULL,
  comments JSON NULL,
  likes JSON NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (review_id),
  CONSTRAINT fk_review_single_details_review
    FOREIGN KEY (review_id) REFERENCES reviews (review_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS read_review_ranges (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  book_id VARCHAR(64) NOT NULL,
  chapter_uid BIGINT NOT NULL,
  range_text VARCHAR(128) NOT NULL,
  bookmark_count INT NULL,
  max_idx INT NULL,
  total_count INT NULL,
  has_more TINYINT NULL,
  synckey BIGINT NULL,
  raw JSON NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_read_review_ranges_range (book_id, chapter_uid, range_text),
  CONSTRAINT fk_read_review_ranges_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS read_review_page_reviews (
  read_review_range_id BIGINT UNSIGNED NOT NULL,
  review_id VARCHAR(191) NOT NULL,
  likes_count INT NULL,
  comments_count INT NULL,
  raw JSON NULL,
  PRIMARY KEY (read_review_range_id, review_id),
  CONSTRAINT fk_read_review_page_reviews_range
    FOREIGN KEY (read_review_range_id) REFERENCES read_review_ranges (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_read_review_page_reviews_review
    FOREIGN KEY (review_id) REFERENCES reviews (review_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reading_stats (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  mode VARCHAR(32) NOT NULL,
  base_time BIGINT NULL,
  read_days INT NULL,
  total_read_time INT NULL,
  day_average_read_time INT NULL,
  compare_value DOUBLE NULL,
  prefer_category_word VARCHAR(1024) NULL,
  prefer_time JSON NULL,
  regist_time BIGINT NULL,
  wr_read_time INT NULL,
  wr_listen_time INT NULL,
  rank_info JSON NULL,
  medals JSON NULL,
  prefer_author JSON NULL,
  prefer_publisher JSON NULL,
  read_records_word VARCHAR(1024) NULL,
  read_distribution_word VARCHAR(1024) NULL,
  raw JSON NULL,
  fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_reading_stats_mode_base_time (mode, base_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reading_stat_daily_times (
  reading_stat_id BIGINT UNSIGNED NOT NULL,
  day_timestamp BIGINT NOT NULL,
  read_time INT NOT NULL DEFAULT 0,
  PRIMARY KEY (reading_stat_id, day_timestamp),
  CONSTRAINT fk_reading_stat_daily_times_stat
    FOREIGN KEY (reading_stat_id) REFERENCES reading_stats (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reading_longest_books (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  reading_stat_id BIGINT UNSIGNED NOT NULL,
  book_id VARCHAR(64) NULL,
  rank_no INT NULL,
  read_time INT NULL,
  tags JSON NULL,
  raw JSON NULL,
  PRIMARY KEY (id),
  KEY idx_reading_longest_books_book (book_id),
  CONSTRAINT fk_reading_longest_books_stat
    FOREIGN KEY (reading_stat_id) REFERENCES reading_stats (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_reading_longest_books_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reading_prefer_categories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  reading_stat_id BIGINT UNSIGNED NOT NULL,
  category_id BIGINT NULL,
  category_title VARCHAR(255) NULL,
  parent_category_id BIGINT NULL,
  parent_category_title VARCHAR(255) NULL,
  reading_count INT NULL,
  reading_time INT NULL,
  raw JSON NULL,
  PRIMARY KEY (id),
  KEY idx_reading_prefer_categories_stat (reading_stat_id),
  CONSTRAINT fk_reading_prefer_categories_stat
    FOREIGN KEY (reading_stat_id) REFERENCES reading_stats (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reading_stat_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  reading_stat_id BIGINT UNSIGNED NOT NULL,
  stat VARCHAR(255) NULL,
  counts VARCHAR(255) NULL,
  raw JSON NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_reading_stat_items_stat
    FOREIGN KEY (reading_stat_id) REFERENCES reading_stats (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reading_prefer_books (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  reading_stat_id BIGINT UNSIGNED NOT NULL,
  type INT NULL,
  title VARCHAR(512) NULL,
  book_id VARCHAR(64) NULL,
  reason VARCHAR(1024) NULL,
  raw JSON NULL,
  PRIMARY KEY (id),
  KEY idx_reading_prefer_books_book (book_id),
  CONSTRAINT fk_reading_prefer_books_stat
    FOREIGN KEY (reading_stat_id) REFERENCES reading_stats (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_reading_prefer_books_book
    FOREIGN KEY (book_id) REFERENCES books (book_id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
