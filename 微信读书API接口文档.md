# 微信读书 API 接口文档

> **API Gateway 基础地址**：`https://i.weread.qq.com/api/agent/gateway`  
> **请求方式**：POST  
> **Content-Type**：`application/json`  
> **鉴权方式**：`Authorization: Bearer wrk-xxxxxxxxx`  
> **通用必传参数**：每次请求 body 必须包含 `"skill_version": "1.0.3"`

---

## 目录

1. [书本信息类](#1-书本信息类)
   - 1.1 [获取书籍基本信息 —— `/book/info`](#11-获取书籍基本信息---bookinfo)
   - 1.2 [获取章节目录 —— `/book/chapterinfo`](#12-获取章节目录---bookchapterinfo)
   - 1.3 [获取阅读进度 —— `/book/getprogress`](#13-获取阅读进度---bookgetprogress)
2. [搜索与推荐类](#2-搜索与推荐类)
   - 2.1 [搜索书籍 —— `/store/search`](#21-搜索书籍---storesearch)
   - 2.2 [个性化推荐 —— `/book/recommend`](#22-个性化推荐---bookrecommend)
   - 2.3 [相似推荐 —— `/book/similar`](#23-相似推荐---booksimilar)
3. [书架与笔记本类](#3-书架与笔记本类)
   - 3.1 [获取书架列表 —— `/shelf/sync`](#31-获取书架列表---shelfsync)
   - 3.2 [获取笔记概览 —— `/user/notebooks`](#32-获取笔记概览---usernotebooks)
4. [划线与标注类](#4-划线与标注类)
   - 4.1 [获取用户划线列表 —— `/book/bookmarklist`](#41-获取用户划线列表---bookbookmarklist)
   - 4.2 [获取热门划线 —— `/book/bestbookmarks`](#42-获取热门划线---bookbestbookmarks)
   - 4.3 [获取划线热度统计 —— `/book/underlines`](#43-获取划线热度统计---bookunderlines)
5. [评论与想法类](#5-评论与想法类)
   - 5.1 [获取公开点评列表 —— `/review/list`](#51-获取公开点评列表---reviewlist)
   - 5.2 [获取个人想法/笔记 —— `/review/list/mine`](#52-获取个人想法笔记---reviewlistmine)
   - 5.3 [获取单条想法详情 —— `/review/single`](#53-获取单条想法详情---reviewsingle)
   - 5.4 [获取划线下的想法列表 —— `/book/readreviews`](#54-获取划线下的想法列表---bookreadreviews)
6. [阅读统计类](#6-阅读统计类)
   - 6.1 [获取阅读统计数据 —— `/readdata/detail`](#61-获取阅读统计数据---readdatadetail)

---

## 1. 书本信息类

### 1.1 获取书籍基本信息 —— `/book/info`

**描述**：获取书籍基本信息，包括书名、作者、评分、分类等。

**是否需要登录**：否

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |

**示例请求**：

```json
{
  "api_name": "/book/info",
  "bookId": "3300144307",
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "bookId": "3300144307",
  "title": "从零构建大模型",
  "author": "[美]塞巴斯蒂安·拉施卡",
  "translator": "覃立波  冯骁骋  刘乾",
  "cover": "https://cdn.weread.qq.com/weread/cover/11/.../t6_....jpg",
  "publisher": "人民邮电出版社有限公司",
  "intro": "本书是关于如何从零开始构建大模型的指南...",
  "newRatingCount": 289,
  "newRating": 915,
  "category": "计算机-人工智能",
  "isbn": "9787115666000",
  "newRatingDetail": {
    "good": 270,
    "fair": 14,
    "poor": 5,
    "recent": 17,
    "deepV": 184,
    "myRating": "",
    "title": "神作潜力"
  },
  "publishTime": "2025-04-01 00:00:00"
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `bookId` | string | 书籍 ID |
| `title` | string | 书名 |
| `author` | string | 作者 |
| `translator` | string | 译者 |
| `cover` | string | 封面图片 URL |
| `publisher` | string | 出版社 |
| `intro` | string | 书籍简介 |
| `category` | string | 分类（如"计算机-人工智能"） |
| `isbn` | string | ISBN 编号 |
| `newRating` | int | 评分（如 915 表示 9.15 分） |
| `newRatingCount` | int | 评分人数 |
| `newRatingDetail` | object | 评分详情 |
| `newRatingDetail.good` | int | 好评数 |
| `newRatingDetail.fair` | int | 一般数 |
| `newRatingDetail.poor` | int | 差评数 |
| `newRatingDetail.recent` | int | 近期评分人数 |
| `newRatingDetail.deepV` | int | 资深会员评分人数 |
| `newRatingDetail.myRating` | string | 我的评分 |
| `newRatingDetail.title` | string | 评分等级标题 |
| `publishTime` | string | 出版时间 |

---

### 1.2 获取章节目录 —— `/book/chapterinfo`

**描述**：获取书籍的完整章节目录，包含章节层级、字数、定价信息。

**是否需要登录**：否

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |

**示例请求**：

```json
{
  "api_name": "/book/chapterinfo",
  "bookId": "3300144307",
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "bookId": "3300144307",
  "synckey": 377876753,
  "chapterUpdateTime": 1760169315,
  "chapters": [
    {
      "chapterUid": 1,
      "chapterIdx": 1,
      "updateTime": 1751005383,
      "level": 1,
      "title": "封面",
      "wordCount": 1,
      "price": 0,
      "isMPChapter": 0,
      "paid": 0
    },
    {
      "chapterUid": 44,
      "chapterIdx": 7,
      "updateTime": 1751005383,
      "level": 1,
      "title": "第1章 理解大语言模型",
      "wordCount": 1043,
      "price": 0,
      "isMPChapter": 0,
      "paid": 0
    },
    {
      "chapterUid": 66,
      "chapterIdx": 29,
      "updateTime": 1751005383,
      "anchors": [
        { "title": "3.3.1 没有可训练权重的简单自注意力机制", "anchor": "sigil_toc_id_1", "level": 3 },
        { "title": "3.3.2 计算所有输入词元的注意力权重", "anchor": "sigil_toc_id_2", "level": 3 }
      ],
      "title": "3.3 通过自注意力机制关注输入的不同部分",
      "wordCount": 6289,
      "price": -1,
      "isMPChapter": 0,
      "paid": 0,
      "level": 2
    }
  ]
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `bookId` | string | 书籍 ID |
| `synckey` | int | 同步版本号 |
| `chapterUpdateTime` | int | 章节最后更新时间(unix 秒级时间戳) |
| `chapters` | array | 章节列表 |
| `chapters[].chapterUid` | int | 章节唯一 ID |
| `chapters[].chapterIdx` | int | 章节序号 |
| `chapters[].level` | int | 章节层级（1=章, 2=节, 3=小节） |
| `chapters[].title` | string | 章节标题 |
| `chapters[].wordCount` | int | 章节字数 |
| `chapters[].price` | int | 价格（-1 表示收费章节） |
| `chapters[].paid` | int | 是否已购买（0=未购买） |
| `chapters[].isMPChapter` | int | 是否公众号文章 |
| `chapters[].anchors` | array | 章节锚点（子标题）列表，可选 |

---

### 1.3 获取阅读进度 —— `/book/getprogress`

**描述**：获取用户对某本书的阅读进度。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |

**示例请求**：

```json
{
  "api_name": "/book/getprogress",
  "bookId": "3300144307",
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "bookId": "3300144307",
  "book": {
    "appId": "wb182564874663h1610147354",
    "bookVersion": 377876753,
    "reviewId": "",
    "chapterUid": 63,
    "chapterOffset": 1304,
    "chapterIdx": 26,
    "updateTime": 1780623926,
    "synckey": 1864501878,
    "summary": "[插图]图3-1　构建大语言模型的3个主",
    "repairOffsetTime": 0,
    "readingTime": 28086,
    "progress": 79,
    "isStartReading": 1,
    "ttsTime": 0,
    "startReadingTime": 1779235401,
    "installId": "3173917231640069191350811534",
    "recordReadingTime": 0
  },
  "timestamp": 1780998575
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `bookId` | string | 书籍 ID |
| `book.progress` | int | 阅读进度百分比（0-100） |
| `book.chapterUid` | int | 当前阅读章节 UID |
| `book.chapterIdx` | int | 当前阅读章节序号 |
| `book.chapterOffset` | int | 章节内阅读偏移量 |
| `book.readingTime` | int | 总阅读时长（秒） |
| `book.startReadingTime` | int | 开始阅读时间(unix 秒级时间戳) |
| `book.updateTime` | int | 最近阅读时间(unix 秒级时间戳) |
| `book.summary` | string | 阅读位置摘要文本 |
| `book.isStartReading` | int | 是否已开始阅读 |
| `book.ttsTime` | int | 听书时长（秒） |
| `timestamp` | int | 服务器返回时间戳 |

---

## 2. 搜索与推荐类

### 2.1 搜索书籍 —— `/store/search`

**描述**：搜索书籍/作者/书单/听书/公众号/文章/全文等，通过 `scope` 切换 tab。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `keyword` | string | 是 | 搜索关键词 |
| `scope` | int | 否 | 搜索类型：0=全部, 10=电子书, 14=微信听书, 6=作者, 12=全文, 13=书单, 2=公众号, 4=文章（默认 10） |
| `maxIdx` | int | 否 | 翻页偏移（默认 0） |
| `count` | int | 否 | 每页数量（不传则为服务端默认值 15） |

**示例请求**：

```json
{
  "api_name": "/store/search",
  "keyword": "三体",
  "scope": 10,
  "count": 10,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "sid": "7oP0fg9XH6",
  "hasMore": 0,
  "results": []
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `sid` | string | 搜索会话 ID |
| `hasMore` | int | 是否有更多结果（0=无, 1=有） |
| `results` | array | 搜索结果列表（scope=10 电子书模式返回书籍对象数组） |

> **注意**：返回的 `results` 字段根据 `scope` 不同，每一项的结构也不同（书籍、作者、文章等）。搜索结果可能为空，建议提高关键词精确度或更换 scope 重试。

---

### 2.2 个性化推荐 —— `/book/recommend`

**描述**：获取个性化推荐书籍（"为你推荐"）。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `count` | int | 否 | 每页数量（默认 12） |
| `maxIdx` | int | 否 | 翻页偏移（默认 0） |

**示例请求**：

```json
{
  "api_name": "/book/recommend",
  "count": 3,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "books": [
    {
      "type": 0,
      "category": "计算机-编程设计",
      "title": "十倍速开发：AI时代的Cursor编程手记",
      "payType": 1048577,
      "intro": "本书是基于 Web 的博客系统 BlogN 的开发过程...",
      "cover": "https://cdn.weread.qq.com/weread/cover/17/.../t6_....jpg",
      "bookId": "3300207566",
      "author": "王尧",
      "price": 57.47
    }
  ]
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `books` | array | 推荐书籍列表 |
| `books[].bookId` | string | 书籍 ID |
| `books[].title` | string | 书名 |
| `books[].author` | string | 作者 |
| `books[].category` | string | 分类 |
| `books[].cover` | string | 封面 URL |
| `books[].intro` | string | 简介 |
| `books[].price` | float | 价格 |
| `books[].payType` | int | 付费类型 |
| `books[].type` | float | 书籍类型 |

---

### 2.3 相似推荐 —— `/book/similar`

**描述**：获取与指定书籍相似的推荐书籍。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |
| `count` | int | 否 | 每页数量（默认 12） |
| `maxIdx` | int | 否 | 翻页偏移（默认 0） |
| `sessionId` | string | 否 | 翻页会话 ID（首次不传，后续用回包中的值） |

**示例请求**：

```json
{
  "api_name": "/book/similar",
  "bookId": "3300144307",
  "count": 12,
  "skill_version": "1.0.3"
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `booksimilar` | object | 相似推荐书籍信息 |

---

## 3. 书架与笔记本类

### 3.1 获取书架列表 —— `/shelf/sync`

**描述**：获取用户的完整书架列表，包含电子书、听书/有声书（专辑）和文章收藏。

**是否需要登录**：是

**请求参数**：无

**示例请求**：

```json
{
  "api_name": "/shelf/sync",
  "skill_version": "1.0.3"
}
```

**返回示例**（精简）：

```json
{
  "books": [
    {
      "bookId": "3300144307",
      "title": "从零构建大模型",
      "author": "[美]塞巴斯蒂安·拉施卡",
      "cover": "https://cdn.weread.qq.com/weread/cover/11/.../t6_....jpg",
      "category": "计算机-人工智能",
      "finishReading": 0,
      "readUpdateTime": 1742302739,
      "secret": 0,
      "updateTime": 1779792615
    }
  ],
  "archive": [
    {
      "bookIds": ["793432", "22791707", "..."],
      "name": "算命",
      "albumIds": []
    },
    {
      "bookIds": ["26831673", "..."],
      "name": "写作",
      "albumIds": []
    }
  ],
  "albums": [
    {
      "albumInfo": {
        "albumId": "3103006161",
        "name": "资治通鉴（白话文）",
        "authorName": "鲸鱼有声",
        "cover": "https://wehear-1258476243.file.myqcloud.com/...",
        "updateTime": 1721378761,
        "finishStatus": "已完结",
        "type": 0,
        "trackCount": 2220,
        "intro": "《资治通鉴》是北宋著名史学家、政治家司马光..."
      },
      "albumInfoExtra": {
        "albumId": "3103006161",
        "secret": 0,
        "lecturePaid": 0,
        "lectureReadUpdateTime": 1742856060,
        "isTop": false
      }
    }
  ],
  "mp": {
    "show": 1,
    "book": {
      "bookId": "mpbook",
      "title": "文章收藏",
      "cover": "https://weread-1258476243.file.myqcloud.com/...",
      "secret": 1,
      "payType": 32,
      "paid": 0,
      "updateTime": 1774248650,
      "readUpdateTime": 1774248650,
      "isTop": false
    }
  }
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `books` | array | 电子书列表 |
| `books[].bookId` | string | 书籍 ID |
| `books[].title` | string | 书名 |
| `books[].author` | string | 作者 |
| `books[].cover` | string | 封面 URL |
| `books[].category` | string | 分类 |
| `books[].finishReading` | int | 是否读完（0=未读完, 1=已读完） |
| `books[].readUpdateTime` | int | 最近阅读时间(unix 秒级时间戳) |
| `books[].secret` | int | 是否私密阅读 |
| `books[].updateTime` | int | 书架更新时间 |
| `archive` | array | 归档分组列表 |
| `archive[].name` | string | 归档分组名 |
| `archive[].bookIds` | array | 该分组下的书籍 ID 列表 |
| `archive[].albumIds` | array | 该分组下的专辑 ID 列表 |
| `albums` | array | 听书/有声书列表 |
| `albums[].albumInfo` | object | 专辑信息 |
| `albums[].albumInfo.albumId` | string | 专辑 ID |
| `albums[].albumInfo.name` | string | 专辑名称 |
| `albums[].albumInfo.authorName` | string | 作者/演播者 |
| `albums[].albumInfo.cover` | string | 封面 URL |
| `albums[].albumInfo.trackCount` | int | 集数 |
| `albums[].albumInfo.finishStatus` | string | 完结状态 |
| `albums[].albumInfoExtra` | object | 专辑额外信息 |
| `mp` | object | 文章收藏（固定为 mpbook） |

---

### 3.2 获取笔记概览 —— `/user/notebooks`

**描述**：获取用户所有有笔记的书籍列表（笔记本概览），含笔记和划线数量统计。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `count` | int | 否 | 每页数量（默认 20） |
| `lastSort` | int | 否 | 翻页游标（上一页最后一条的 sort 值） |

**示例请求**：

```json
{
  "api_name": "/user/notebooks",
  "count": 3,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "synckey": 1780923584,
  "totalBookCount": 100,
  "noBookReviewCount": 3,
  "hasMore": 1,
  "totalNoteCount": 410,
  "books": [
    {
      "bookId": "3300144307",
      "book": {
        "bookId": "3300144307",
        "title": "从零构建大模型",
        "author": "[美]塞巴斯蒂安·拉施卡",
        "translator": "覃立波  冯骁骋  刘乾",
        "cover": "https://cdn.weread.qq.com/weread/cover/11/.../t6_....jpg",
        "version": 377876753,
        "format": "epub",
        "type": 0,
        "price": 54.9,
        "payType": 1048577,
        "categories": [{"categoryId": 700000, "subCategoryId": 700005, "categoryType": 0, "title": "计算机-人工智能"}],
        "publishTime": "2025-04-01 00:00:00",
        "lastChapterIdx": 76,
        "finished": 1
      },
      "reviewCount": 4,
      "markedStatus": 2,
      "readingProgress": 79,
      "noteCount": 1,
      "bookmarkCount": 0,
      "sort": 1779847488
    }
  ]
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `synckey` | int | 同步版本号 |
| `totalBookCount` | int | 笔记本总数 |
| `totalNoteCount` | int | 笔记总数 |
| `noBookReviewCount` | int | 未归类书评数 |
| `hasMore` | int | 是否有更多 |
| `books` | array | 笔记本列表 |
| `books[].bookId` | string | 书籍 ID |
| `books[].book` | object | 完整书籍信息 |
| `books[].reviewCount` | int | 想法/笔记数 |
| `books[].markedStatus` | int | 标记状态 |
| `books[].readingProgress` | int | 阅读进度百分比 |
| `books[].noteCount` | int | 笔记数 |
| `books[].bookmarkCount` | int | 划线数 |
| `books[].sort` | int | 排序值（翻页游标使用） |

---

## 4. 划线与标注类

### 4.1 获取用户划线列表 —— `/book/bookmarklist`

**描述**：获取用户对某本书的划线列表（不含书签）。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |

**示例请求**：

```json
{
  "api_name": "/book/bookmarklist",
  "bookId": "3300144307",
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "synckey": 1779786053,
  "updated": [
    {
      "bookId": "3300144307",
      "chapterIdx": 27,
      "bookmarkId": "3300144307_64_2196-2233",
      "range": "2196-2233",
      "markText": "只需记住，编码器-解码器RNN存在的缺陷对注意力机制的设计起到了促进作用。",
      "colorStyle": 0,
      "type": 1,
      "chapterUid": 64,
      "createTime": 1779586896
    }
  ],
  "removed": [],
  "chapters": [
    {
      "title": "3.1 长序列建模中的问题",
      "chapterUid": 64,
      "chapterIdx": 27
    }
  ],
  "book": {
    "bookId": "3300144307",
    "version": 377876753,
    "format": "epub",
    "title": "从零构建大模型",
    "author": "[美]塞巴斯蒂安·拉施卡",
    "cover": "https://cdn.weread.qq.com/weread/cover/11/.../s_....jpg"
  }
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `synckey` | int | 同步版本号 |
| `updated` | array | 新增/更新的划线列表 |
| `updated[].bookmarkId` | string | 划线唯一 ID |
| `updated[].range` | string | 划线范围（"起始-结束"格式，用于深度链接） |
| `updated[].markText` | string | 划线文本内容 |
| `updated[].chapterUid` | int | 所属章节 UID |
| `updated[].chapterIdx` | int | 所属章节序号 |
| `updated[].colorStyle` | int | 划线颜色样式 |
| `updated[].type` | int | 划线类型 |
| `updated[].createTime` | int | 创建时间(unix 秒级时间戳) |
| `removed` | array | 已删除的划线列表 |
| `chapters` | array | 划线涉及的章节信息 |
| `book` | object | 书籍基本信息 |

---

### 4.2 获取热门划线 —— `/book/bestbookmarks`

**描述**：获取某本书的热门划线列表，包含划线文本和划线人数，按热度排序，最多 20 条。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |
| `chapterUid` | int | 否 | 章节 UID（0=全部章节，默认 0） |
| `synckey` | int | 否 | 增量同步 key（默认 0） |

**示例请求**：

```json
{
  "api_name": "/book/bestbookmarks",
  "bookId": "3300144307",
  "chapterUid": 0,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "synckey": 1780994348,
  "totalCount": 380,
  "items": [
    {
      "bookId": "3300144307",
      "userVid": 17755735,
      "bookmarkId": "3300144307_44_1076-1148",
      "chapterUid": 44,
      "range": "1076-1148",
      "simplifiedRange": "",
      "traditionalRange": "",
      "markText": "当我们谈论语言模型的"理解"能力时，实际上是指它们能够处理和生成看似连贯且符合语境的文本...",
      "totalCount": 615
    }
  ],
  "chapters": [
    {
      "bookId": "3300144307",
      "chapterUid": 44,
      "chapterIdx": 7,
      "title": "第1章 理解大语言模型"
    }
  ]
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `synckey` | int | 同步版本号 |
| `totalCount` | int | 总热门划线数 |
| `items` | array | 热门划线列表 |
| `items[].bookmarkId` | string | 划线唯一 ID |
| `items[].markText` | string | 划线文本内容 |
| `items[].totalCount` | int | 该划线被划线人数（热度） |
| `items[].userVid` | int | 首次划线用户 VID |
| `items[].chapterUid` | int | 所属章节 UID |
| `items[].range` | string | 划线范围 |
| `chapters` | array | 划线涉及的章节信息 |

---

### 4.3 获取划线热度统计 —— `/book/underlines`

**描述**：获取某本书某章节的划线热度统计，包含每条划线的人数/得分/类型，不含划线文本。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |
| `chapterUid` | int | 是 | 章节 UID（从 `/book/chapterinfo` 获取） |
| `synckey` | int | 否 | 增量同步 key（默认 0） |

**示例请求**：

```json
{
  "api_name": "/book/underlines",
  "bookId": "3300144307",
  "chapterUid": 44,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "synckey": 1780994348,
  "bookId": "3300144307",
  "chapterUid": 44,
  "underlines": [
    {
      "count": 0,
      "score": 0.8844891786575317,
      "type": 0,
      "range": "536-552"
    },
    {
      "count": 615,
      "score": 22.781740188598634,
      "type": 2,
      "range": "1076-1148"
    }
  ]
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `synckey` | int | 同步版本号 |
| `bookId` | string | 书籍 ID |
| `chapterUid` | int | 章节 UID |
| `underlines` | array | 划线热度列表 |
| `underlines[].range` | string | 划线范围 |
| `underlines[].count` | int | 划线人数 |
| `underlines[].score` | float | 热度得分 |
| `underlines[].type` | int | 划线类型（0=普通, 2=热门） |

---

## 5. 评论与想法类

### 5.1 获取公开点评列表 —— `/review/list`

**描述**：获取某本书的公开点评/想法列表。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |
| `reviewListType` | int | 否 | 筛选类型：0=全部, 1=推荐, 2=不行, 3=最新, 4=一般（默认 0） |
| `count` | int | 否 | 每页数量（默认 20） |
| `maxIdx` | int | 否 | 翻页偏移（默认 0） |
| `synckey` | int | 否 | 翻页游标（默认 0） |

**示例请求**：

```json
{
  "api_name": "/review/list",
  "bookId": "3300144307",
  "count": 3,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "synckey": 1780998584,
  "reviews": [
    {
      "idx": 1,
      "review": {
        "reviewId": "18008078_80HoaKhYZ",
        "review": {
          "abstract": "",
          "content": "Github上很火的开源项目LLMs-from-scratch，中文版纸书4月份才上市...",
          "range": "",
          "book": {
            "bookId": "3300144307",
            "title": "从零构建大模型",
            "author": "[美]塞巴斯蒂安·拉施卡"
          },
          "star": 100,
          "isFinish": 1,
          "author": {
            "name": "迷途小書僮",
            "avatar": "https://res.weread.qq.com/wravatar/...",
            "userVid": 18008078
          },
          "htmlContent": "Github上很火的开源项目LLMs-from-scratch...",
          "createTime": 1749185401
        },
        "likesCount": 319,
        "commentsCount": 16
      }
    }
  ],
  "reviewsHasMore": 1,
  "reviewsHas5Star": 1,
  "reviewsHas1Star": 0,
  "reviewsHasRecent": 0,
  "reviewsCnt": 185,
  "recentTotalCnt": 17,
  "friendCommentCount": 0,
  "friendUniqueCount": 0,
  "deepVRecommendInfo": {
    "title": "184 个资深会员点评",
    "subtitle": "其中 172 人(93.5%)推荐本书"
  },
  "deepVRecommendValue": 935,
  "deepVUniqueCount": 184
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `synckey` | int | 同步版本号 |
| `reviews` | array | 点评列表 |
| `reviews[].review.reviewId` | string | 点评/想法 ID |
| `reviews[].review.content` | string | 点评文本内容 |
| `reviews[].review.htmlContent` | string | HTML 格式内容 |
| `reviews[].review.star` | int | 评分（0-100） |
| `reviews[].review.isFinish` | int | 是否读完 |
| `reviews[].review.createTime` | int | 创建时间(unix 秒级时间戳) |
| `reviews[].review.author` | object | 作者信息（name/avatar/userVid） |
| `reviews[].review.book` | object | 关联书籍信息 |
| `reviews[].likesCount` | int | 点赞数 |
| `reviews[].commentsCount` | int | 评论数 |
| `reviewsHasMore` | int | 是否有更多点评 |
| `reviewsHas5Star` | int | 是否有 5 星好评 |
| `reviewsHas1Star` | int | 是否有 1 星差评 |
| `reviewsCnt` | int | 点评总数 |
| `recentTotalCnt` | int | 近期点评数 |
| `friendCommentCount` | int | 好友评论数 |
| `deepVRecommendInfo` | object | 资深会员推荐信息 |
| `deepVRecommendValue` | int | 资深会员推荐值 |
| `deepVUniqueCount` | int | 资深会员评论人数 |

---

### 5.2 获取个人想法/笔记 —— `/review/list/mine`

**描述**：获取用户在某本书上的个人想法/笔记（含划线、手绘笔记等）。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookid` | string | 是 | 书籍 ID（注意字段名是 `bookid`，小写 d） |
| `synckey` | int | 否 | 翻页游标（默认 0） |
| `count` | int | 否 | 每页数量（默认 20） |

**示例请求**：

```json
{
  "api_name": "/review/list/mine",
  "bookid": "3300144307",
  "count": 3,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "synckey": 1779847592,
  "totalCount": 4,
  "reviews": [
    {
      "reviewId": "4081963_89pddhSWU",
      "review": {
        "abstract": "3.5 利用因果注意力隐藏未来词汇...",
        "bookId": "3300144307",
        "bookVersion": 377876753,
        "chapterName": "3.5 利用因果注意力隐藏未来词汇",
        "chapterUid": 68,
        "colorStyle": 0,
        "content": "",
        "htmlContent": "",
        "isPrivate": 1,
        "pencilNote": {
          "andDrawingUrl": "https://weread-picture-1258476243.file.myqcloud.com/...",
          "contextAbstract": "",
          "doddleDrawingUrl": "",
          "drawingUrl": "",
          "imageHeight": 1440,
          "imageUrl": "https://weread-picture-1258476243.file.myqcloud.com/...",
          "imageWidth": 1400,
          "rangeEnd": -2147483648,
          "rangeStart": -2147483648,
          "type": 0,
          "updateTime": 1779847486210
        },
        "range": "355",
        "createTime": 1779847488,
        "title": "",
        "type": 1,
        "chapterIdx": 31,
        "author": {
          "userVid": 4081963,
          "name": "郭享",
          "avatar": "https://res.weread.qq.com/wravatar/..."
        }
      }
    }
  ],
  "removed": [],
  "hasMore": 0
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `synckey` | int | 同步版本号 |
| `totalCount` | int | 总笔记数 |
| `hasMore` | int | 是否有更多 |
| `reviews` | array | 个人笔记列表 |
| `reviews[].reviewId` | string | 笔记/想法 ID |
| `reviews[].review.abstract` | string | 摘要（划线文本） |
| `reviews[].review.content` | string | 笔记文本内容 |
| `reviews[].review.htmlContent` | string | HTML 格式内容 |
| `reviews[].review.isPrivate` | int | 是否私密 |
| `reviews[].review.chapterUid` | int | 所属章节 UID |
| `reviews[].review.chapterName` | string | 所属章节名称 |
| `reviews[].review.range` | string | 划线范围 |
| `reviews[].review.createTime` | int | 创建时间(unix 秒级时间戳) |
| `reviews[].review.type` | int | 类型（1=笔记, 4=点评） |
| `reviews[].review.pencilNote` | object | 手绘笔记信息（如果有） |
| `reviews[].review.pencilNote.imageUrl` | string | 手绘图片 URL |
| `reviews[].review.pencilNote.andDrawingUrl` | string | 附带绘图 URL |
| `reviews[].review.pencilNote.doddleDrawingUrl` | string | 涂鸦绘图 URL |
| `reviews[].review.author` | object | 用户信息 |

---

### 5.3 获取单条想法详情 —— `/review/single`

**描述**：获取单条想法/评论的详情，含评论列表和点赞信息。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `reviewId` | string | 是 | 想法/评论 ID |
| `commentsCount` | int | 否 | 拉取评论数量（默认 10） |
| `commentsDirection` | int | 否 | 评论排序：0=倒序, 1=正序（默认 1） |
| `likesCount` | int | 否 | 拉取点赞数量（默认 10） |
| `likesDirection` | int | 否 | 点赞排序：0=倒序（默认 0） |
| `synckey` | int | 否 | 增量同步 key（默认 0） |

**示例请求**：

```json
{
  "api_name": "/review/single",
  "reviewId": "18008078_80HoaKhYZ",
  "commentsCount": 2,
  "likesCount": 2,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "reviewId": "18008078_80HoaKhYZ",
  "review": {
    "abstract": "",
    "bookId": "3300144307",
    "content": "Github上很火的开源项目LLMs-from-scratch...",
    "author": {
      "userVid": 18008078,
      "name": "迷途小書僮",
      "avatar": "https://res.weread.qq.com/wravatar/...",
      "isFollowing": 0,
      "isFollower": 0,
      "isDeepV": true,
      "deepVTitle": "资深会员",
      "medalInfo": {
        "id": "M1-0-365",
        "desc": "连续阅读",
        "title": "连续阅读",
        "levelIndex": 365
      }
    },
    "isPrivate": 0,
    "range": "",
    "star": 100,
    "type": 4,
    "createTime": 1749185401,
    "isFinish": 1,
    "isDeepV": 1,
    "book": {
      "bookId": "3300144307",
      "title": "从零构建大模型",
      "author": "[美]塞巴斯蒂安·拉施卡"
    }
  },
  "htmlContent": "Github上很火的开源项目LLMs-from-scratch...",
  "synckey": 1780643535
}
```

**返回字段说明**（核心字段）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `reviewId` | string | 想法/评论 ID |
| `review.content` | string | 文本内容 |
| `review.htmlContent` | string | HTML 格式内容 |
| `review.star` | int | 评分（0-100） |
| `review.isFinish` | int | 是否读完 |
| `review.isPrivate` | int | 是否私密 |
| `review.isDeepV` | int | 是否资深会员 |
| `review.type` | int | 类型（1=笔记, 4=点评/书评） |
| `review.createTime` | int | 创建时间(unix 秒级时间戳) |
| `review.author` | object | 作者信息（含勋章 medalInfo） |
| `synckey` | int | 同步版本号 |

---

### 5.4 获取划线下的想法列表 —— `/book/readreviews`

**描述**：获取章节中某些划线范围下的想法/评论列表。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `bookId` | string | 是 | 书籍 ID |
| `chapterUid` | int | 是 | 章节 UID |
| `reviews` | array | 是 | 要查询的划线范围数组 |

**reviews 数组项说明**：

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `range` | string | 是 | 划线范围（如 "1076-1148"） |
| `maxIdx` | int | 是 | 翻页偏移 |
| `count` | int | 是 | 拉取数量 |
| `synckey` | int | 是 | 同步 key |

**示例请求**：

```json
{
  "api_name": "/book/readreviews",
  "bookId": "3300144307",
  "chapterUid": 44,
  "reviews": [
    {
      "range": "1076-1148",
      "maxIdx": 0,
      "count": 3,
      "synckey": 0
    }
  ],
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "bookId": "3300144307",
  "chapterUid": 44,
  "reviews": [
    {
      "range": "1076-1148",
      "bookMarkCount": 615,
      "maxIdx": 3,
      "totalCount": 60,
      "hasMore": 1,
      "synckey": 1780994348,
      "pageReviews": [
        {
          "reviewId": "17755735_89EyWT2vL",
          "review": {
            "abstract": "当我们谈论语言模型的"理解"能力时...",
            "bookId": "3300144307",
            "chapterName": "第1章 理解大语言模型",
            "chapterUid": 44,
            "content": "管他有没有意识或理解能力呢...",
            "isPrivate": 0,
            "range": "1076-1148",
            "createTime": 1780719404,
            "type": 1,
            "author": {
              "userVid": 17755735,
              "name": "ᝰꫛꫀꪝ",
              "avatar": "https://thirdwx.qlogo.cn/..."
            }
          },
          "likesCount": 35,
          "commentsCount": 1
        }
      ]
    }
  ]
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `bookId` | string | 书籍 ID |
| `chapterUid` | int | 章节 UID |
| `reviews` | array | 划线范围对应的想法列表 |
| `reviews[].range` | string | 划线范围 |
| `reviews[].bookMarkCount` | int | 该划线被划线人数 |
| `reviews[].totalCount` | int | 该划线下想法总数 |
| `reviews[].hasMore` | int | 是否有更多 |
| `reviews[].maxIdx` | int | 翻页游标 |
| `reviews[].pageReviews` | array | 想法详情列表 |
| `reviews[].pageReviews[].reviewId` | string | 想法 ID |
| `reviews[].pageReviews[].review.content` | string | 想法内容 |
| `reviews[].pageReviews[].review.abstract` | string | 引用的划线文本 |
| `reviews[].pageReviews[].likesCount` | int | 点赞数 |
| `reviews[].pageReviews[].commentsCount` | int | 评论数 |

---

## 6. 阅读统计类

### 6.1 获取阅读统计数据 —— `/readdata/detail`

**描述**：获取用户阅读统计数据，支持周/月/年/总维度，包含阅读时长、天数、书籍排行、偏好分析等。

**是否需要登录**：是

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `mode` | string | 否 | 统计维度：`weekly`=本周, `monthly`=本月, `annually`=本年, `overall`=总计（默认 `monthly`） |
| `baseTime` | int | 否 | 基准时间戳（0=当前周期，传历史时间戳可查看历史周期数据，默认 0） |

**示例请求**：

```json
{
  "api_name": "/readdata/detail",
  "mode": "monthly",
  "baseTime": 0,
  "skill_version": "1.0.3"
}
```

**返回示例**：

```json
{
  "readTimes": {
    "1780243200": 33,
    "1780329600": 241,
    "1780416000": 1,
    "1780502400": 1110,
    "1780588800": 0,
    "1780675200": 4
  },
  "readDays": 2,
  "totalReadTime": 1389,
  "dayAverageReadTime": 154,
  "compare": -0.9858430734329536,
  "baseTime": 1780243200,
  "readLongest": [
    {
      "book": {
        "bookId": "3300144307",
        "title": "从零构建大模型",
        "author": "[美]塞巴斯蒂安·拉施卡",
        "cover": "https://cdn.weread.qq.com/weread/cover/11/.../s_....jpg",
        "publishTime": "2025-04-01 00:00:00"
      },
      "readTime": 1110,
      "tags": ["单日阅读最久"]
    }
  ],
  "preferCategory": [
    {
      "categoryId": 700000,
      "categoryTitle": "计算机",
      "parentCategoryId": 700000,
      "parentCategoryTitle": "计算机",
      "readingCount": 1,
      "readingTime": 1110
    }
  ],
  "preferCategoryWord": "偏好阅读计算机",
  "readStat": [
    { "stat": "读过", "counts": "1本" },
    { "stat": "读完", "counts": "0本" },
    { "stat": "阅读", "counts": "2天" },
    { "stat": "笔记", "counts": "0条" }
  ],
  "registTime": 1498385160,
  "wrReadTime": 0,
  "wrListenTime": 0,
  "rank": null,
  "preferBooks": [
    { "type": 13, "title": "我的最爱" },
    { "type": 1, "title": "近期偏爱" },
    {
      "type": 6,
      "title": "最爱计算机",
      "bookInfo": {
        "bookId": "3300144307",
        "title": "从零构建大模型",
        "author": "[美]塞巴斯蒂安·拉施卡"
      },
      "reason": "阅读了7小时"
    }
  ],
  "medals": null,
  "preferAuthor": null,
  "preferPublisher": null,
  "readRecordsWord": "书籍分布",
  "readDistributionWord": "点评分布"
}
```

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `readTimes` | object | 每日阅读时长（key 为日期时间戳，value 为阅读秒数） |
| `readDays` | int | 阅读天数 |
| `totalReadTime` | int | 总阅读时长（秒） |
| `dayAverageReadTime` | int | 日均阅读时长（秒） |
| `compare` | float | 与上期比较（负数=减少，如 -0.98 表示减少 98%） |
| `baseTime` | int | 基准时间(unix 秒级时间戳) |
| `readLongest` | array | 阅读最久的书籍排行 |
| `readLongest[].book` | object | 书籍信息 |
| `readLongest[].readTime` | int | 阅读时长（秒） |
| `readLongest[].tags` | array | 标签（如["单日阅读最久"]） |
| `preferCategory` | array | 偏好分类统计 |
| `preferCategory[].categoryTitle` | string | 分类名称 |
| `preferCategory[].readingCount` | int | 阅读本数 |
| `preferCategory[].readingTime` | int | 阅读时长（秒） |
| `preferCategoryWord` | string | 偏好分类的文本描述 |
| `preferTime` | object | 偏好的阅读时段 |
| `readStat` | array | 阅读统计概览（读过/读完/阅读/笔记） |
| `registTime` | int | 注册时间(unix 秒级时间戳) |
| `wrReadTime` | int | 微信读书阅读时长（秒） |
| `wrListenTime` | int | 微信读书听书时长（秒） |
| `preferBooks` | array | 偏好书籍排行 |
| `rank` | object | 用户排行信息 |
| `medals` | object | 勋章信息 |

---

## 附录：通用返回错误码

| errcode | 说明 |
|---------|------|
| `0` | 成功 |
| `-2003` | 参数格式错误 |
| `非 0` | 请求失败，`errmsg` 字段包含中文错误提示 |

---

## 附录：通用说明

### 版本上報

每次请求 body 必须包含 `"skill_version": "1.0.3"`。如果回包中出现 `upgrade_info` 字段，必须立即暂停当前操作，按照指引完成升级。

### 参数平铺

业务参数必须和 `api_name`、`skill_version` 放在同一层，不要包在 `params`、`data`、`body` 等对象里。

### 深度链接（URL Schema）

| 场景 | 链接格式 |
|------|----------|
| 打开书籍 | `weread://reading?bId={bookId}` |
| 跳转指定章节 | `weread://reading?bId={bookId}&chapterUid={chapterUid}` |
| 跳转划线/想法位置 | `weread://bestbookmark?bookId={bookId}&chapterUid={chapterUid}&rangeStart={rangeStart}&rangeEnd={rangeEnd}&userVid={userVid}` |
