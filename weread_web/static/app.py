const { createApp } = Vue;

const iconTick = () => {
  var retry = 0;
  var attempt = function() {
    if (window.lucide && window.lucide.createIcons) {
      window.lucide.createIcons();
      return;
    }
    if (++retry < 20) setTimeout(attempt, 150);
  };
  setTimeout(attempt, 50);
};

const formatters = {
  number(value) {
    if (value === null || value === undefined || value === "") return "0";
    return new Intl.NumberFormat("zh-CN").format(value);
  },
  duration(seconds) {
    if (!seconds) return "0 分钟";
    const minutes = Math.round(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const rest = minutes % 60;
    if (!hours) return `${minutes} 分钟`;
    return rest ? `${hours} 小时 ${rest} 分钟` : `${hours} 小时`;
  },
  hours(seconds) {
    if (!seconds) return "0 小时";
    const hours = seconds / 3600;
    return hours >= 100 ? `${Math.round(hours)} 小时` : `${Math.round(hours * 10) / 10} 小时`;
  },
  dateTime(value) {
    if (!value) return "暂无同步记录";
    return new Date(value).toLocaleString("zh-CN", { hour12: false });
  },
  date(timestamp) {
    if (!timestamp) return "";
    return new Date(timestamp * 1000).toLocaleDateString("zh-CN");
  },
  percent(value) {
    const number = Math.max(0, Math.min(100, Number(value || 0)));
    return `${number}%`;
  },
};

const Icon = {
  props: ["name", "size"],
  mounted: iconTick,
  updated: iconTick,
  template: `<i class="icon" :data-lucide="name" :style="{ width: (size || 18) + 'px', height: (size || 18) + 'px' }"></i>`,
};

const AppSidebar = {
  components: { Icon },
  props: ["view", "summary", "navItems"],
  emits: ["change-view"],
  methods: formatters,
  template: `
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark"><icon name="book-open" :size="22"></icon></div>
        <div>
          <h1>郭享的微信读书</h1>
          <p>个人阅读数据</p>
        </div>
      </div>

      <nav class="nav" aria-label="页面导航">
        <button
          v-for="item in navItems"
          :key="item.key"
          :class="{ active: view === item.key }"
          type="button"
          @click="$emit('change-view', item.key)"
        >
          <icon :name="item.icon"></icon>
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div class="sidebar-stat">
        <span>藏书总量</span>
        <strong>{{ number(summary.counts.books) }}</strong>
        <small>{{ number(summary.counts.bookmarks) }} 条划线 · {{ number(summary.counts.reviews) }} 条笔记</small>
      </div>

      <div class="sync">
        <span>最近同步</span>
        <strong>{{ dateTime(summary.latest_sync) }}</strong>
      </div>
    </aside>
  `,
};

const PageHeader = {
  components: { Icon },
  props: ["title", "subtitle", "summary"],
  emits: ["refresh"],
  methods: formatters,
  template: `
    <section class="topbar">
      <div>
        <p class="eyebrow">WeRead Personal Dashboard</p>
        <h2>{{ title }}</h2>
        <p class="subtitle">{{ subtitle }}</p>
      </div>
      <button class="icon-button" type="button" title="刷新数据" @click="$emit('refresh')">
        <icon name="refresh-cw"></icon>
      </button>
    </section>
  `,
};

const MetricCard = {
  components: { Icon },
  props: ["label", "value", "hint", "format", "icon"],
  methods: formatters,
  computed: {
    displayValue() {
      if (this.format === "hours") return this.hours(this.value);
      if (this.format === "duration") return this.duration(this.value);
      return this.number(this.value);
    },
  },
  template: `
    <article class="metric">
      <div class="metric-icon"><icon :name="icon"></icon></div>
      <span>{{ label }}</span>
      <strong>{{ displayValue }}</strong>
      <small>{{ hint }}</small>
    </article>
  `,
};

const ReadingStats = {
  components: { Icon },
  props: ["summary"],
  emits: ["open-page"],
  methods: formatters,
  template: `
    <section class="panel stat-panel">
      <div class="panel-title">
        <div>
          <h3>阅读统计</h3>
          <p>累计时长、活跃天数和日均阅读</p>
        </div>
        <button class="text-button" type="button" @click="$emit('open-page', 'notes')">
          <icon name="notebook-pen"></icon>
          <span>查看笔记</span>
        </button>
      </div>
      <dl class="stats-list">
        <div>
          <dt>阅读天数</dt>
          <dd>{{ number(summary.all_time_stats && summary.all_time_stats.read_days) }} 天</dd>
        </div>
        <div>
          <dt>总阅读时长</dt>
          <dd>{{ hours(summary.all_time_stats && summary.all_time_stats.total_read_time) }}</dd>
        </div>
        <div>
          <dt>日均阅读</dt>
          <dd>{{ duration(summary.all_time_stats && summary.all_time_stats.day_average_read_time) }}</dd>
        </div>
        <div>
          <dt>有记录书籍</dt>
          <dd>{{ number(summary.all_time_stats && summary.all_time_stats.read_books) }} 本</dd>
        </div>
      </dl>
    </section>
  `,
};

const CurrentReading = {
  components: { Icon },
  props: ["items", "fallbackCover"],
  emits: ["select-book"],
  methods: formatters,
  template: `
    <section class="panel current-panel">
      <div class="panel-title">
        <div>
          <h3>最近在读</h3>
          <p>点击书籍查看划线和笔记</p>
        </div>
        <span class="panel-count">{{ items.length }} 本</span>
      </div>
      <div class="reading-list">
        <button class="reading-item" v-for="book in items" :key="book.book_id" type="button" @click="$emit('select-book', book.book_id)">
          <img :src="book.cover || fallbackCover" :alt="book.title || '封面'" loading="lazy" />
          <div>
            <strong>{{ book.title || '未命名' }}</strong>
            <span>{{ book.author || '未知作者' }}</span>
            <div class="mini-progress">
              <i :style="{ width: percent(book.progress) }"></i>
            </div>
            <small>{{ book.progress || 0 }}% · {{ duration(book.reading_time) }}</small>
          </div>
        </button>
        <p class="empty-state" v-if="!items.length">暂无正在阅读的书</p>
      </div>
    </section>
  `,
};

const ReadingHeatmap = {
  props: ["heatmap"],
  data() {
    return { selectedDate: "" };
  },
  watch: {
    heatmap: {
      handler(next) {
        const days = this.buildYearDays(next);
        const todayText = this.dateToText(new Date());
        const today = days.find((day) => day.date === todayText);
        const activeLatest = [...days].reverse().find((day) => day.read_time > 0);
        const fallback = today || activeLatest || days[days.length - 1];
        this.selectedDate = fallback ? fallback.date : "";
      },
      immediate: true,
    },
  },
  methods: {
    ...formatters,
    extractYearDays(source) {
      return (source.months || []).flatMap((month) => month.days || []);
    },
    dateToText(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    },
    buildYearDays(source) {
      const sourceDays = this.extractYearDays(source);
      const year = source.year || new Date().getFullYear();
      const byDate = new Map(sourceDays.map((day) => [day.date, day]));
      const maxReadTime = Math.max(source.max_read_time || 0, ...sourceDays.map((day) => day.read_time || 0), 0);
      const days = [];
      const cursor = new Date(year, 0, 1);
      while (cursor.getFullYear() === year) {
        const month = String(cursor.getMonth() + 1).padStart(2, "0");
        const date = String(cursor.getDate()).padStart(2, "0");
        const dateText = `${year}-${month}-${date}`;
        const existing = byDate.get(dateText);
        const readTime = existing ? existing.read_time || 0 : 0;
        let level = existing ? existing.level || 0 : 0;
        if (!level && readTime > 0 && maxReadTime > 0) {
          level = Math.min(4, Math.max(1, Math.ceil((readTime / maxReadTime) * 4)));
        }
        days.push({
          date: dateText,
          timestamp: Math.floor(cursor.getTime() / 1000),
          read_time: readTime,
          level,
          weekday: (cursor.getDay() + 6) % 7,
        });
        cursor.setDate(cursor.getDate() + 1);
      }
      return days;
    },
    heatmapDuration(seconds) {
      if (!seconds) return "0 分钟";
      if (seconds < 60) return `${seconds} 秒`;
      return this.duration(seconds);
    },
    selectDay(day) {
      if (!day || day.blank) return;
      this.selectedDate = day.date;
    },
    tooltip(day) {
      return `${this.formatFullDate(day.date)}，阅读 ${this.heatmapDuration(day.read_time)}`;
    },
    formatFullDate(dateText) {
      if (!dateText) return "暂无日期";
      const [year, month, day] = dateText.split("-").map(Number);
      return `${year}年${month}月${day}日`;
    },
    shortDate(dateText) {
      if (!dateText) return "";
      const [, month, day] = dateText.split("-").map(Number);
      return `${month}/${day}`;
    },
  },
  computed: {
    yearDays() {
      return this.buildYearDays(this.heatmap);
    },
    calendarCells() {
      const days = this.yearDays;
      if (!days.length) return [];
      const leadingBlanks = Array.from({ length: days[0].weekday || 0 }, (_, index) => ({
        blank: true,
        key: `leading-${index}`,
      }));
      const cells = [...leadingBlanks, ...days];
      const trailingBlanks = Array.from({ length: (7 - (cells.length % 7)) % 7 }, (_, index) => ({
        blank: true,
        key: `trailing-${index}`,
      }));
      return [...cells, ...trailingBlanks];
    },
    weekCount() {
      return Math.max(1, Math.ceil(this.calendarCells.length / 7));
    },
    monthMarkers() {
      const days = this.yearDays;
      const year = this.heatmap.year || new Date().getFullYear();
      const offset = days[0] ? days[0].weekday || 0 : 0;
      return Array.from({ length: 12 }, (_, index) => {
        const month = index + 1;
        const firstDate = `${year}-${String(month).padStart(2, "0")}-01`;
        const dayIndex = days.findIndex((day) => day.date === firstDate);
        return {
          key: firstDate,
          label: `${month}月`,
          gridColumn: dayIndex >= 0 ? Math.floor((dayIndex + offset) / 7) + 1 : 1,
        };
      });
    },
    selectedDay() {
      return this.yearDays.find((day) => day.date === this.selectedDate) || null;
    },
    selectedLabel() {
      return this.selectedDay ? this.formatFullDate(this.selectedDay.date) : "请选择一天";
    },
    weekDays() {
      if (!this.selectedDay) return [];
      const index = this.yearDays.findIndex((day) => day.date === this.selectedDay.date);
      if (index < 0) return [];
      const start = index - this.selectedDay.weekday;
      return Array.from({ length: 7 }, (_, offset) => {
        const day = this.yearDays[start + offset];
        return day || {
          date: "",
          read_time: 0,
          weekday: offset,
          outside: true,
        };
      });
    },
    weekMaxReadTime() {
      return Math.max(...this.weekDays.map((day) => day.read_time || 0), 1);
    },
    weekTotalReadTime() {
      return this.weekDays.reduce((sum, day) => sum + (day.read_time || 0), 0);
    },
  },
  template: `
    <section class="panel heatmap-panel">
      <div class="panel-title">
        <div>
          <h3>全年阅读热力图</h3>
          <p>{{ heatmap.year || '暂无' }} 年 · 点击任意一天查看具体日期</p>
        </div>
        <span class="panel-count">{{ heatmap.active_days || 0 }} 天阅读</span>
      </div>

      <div class="heatmap-selected">
        <strong>{{ selectedLabel }}</strong>
        <span v-if="selectedDay">阅读 {{ heatmapDuration(selectedDay.read_time) }}</span>
        <span v-else>暂无阅读记录</span>
        <span>全年累计 {{ heatmapDuration(heatmap.total_read_time) }}</span>
        <span>峰值 {{ heatmapDuration(heatmap.max_read_time) }}</span>
      </div>

      <div class="year-heatmap">
        <div class="year-heatmap-grid" :style="{ gridTemplateColumns: 'repeat(' + weekCount + ', minmax(0, 1fr))' }">
          <button
            v-for="(day, index) in calendarCells"
            :key="day.date || day.key || index"
            class="heat-cell"
            type="button"
            :class="{ blank: day.blank, selected: selectedDay && day.date === selectedDay.date }"
            :data-level="day.level || 0"
            :title="day.blank ? '' : tooltip(day)"
            @click="selectDay(day)"
          ></button>
          <p class="empty-state heatmap-empty" v-if="!calendarCells.length">暂无阅读记录</p>
        </div>
      </div>

      <div class="weekly-bars">
        <div class="weekly-bars-title">
          <strong>本周阅读时长</strong>
          <span>累计 {{ heatmapDuration(weekTotalReadTime) }}</span>
        </div>
        <div class="weekly-bar-grid">
          <div
            class="weekly-bar-item"
            v-for="(day, index) in weekDays"
            :key="day.date || index"
            :class="{ active: selectedDay && day.date === selectedDay.date, outside: day.outside }"
          >
            <div class="weekly-bar-track" :title="day.date ? tooltip(day) : ''">
              <i :style="{ height: Math.max(4, Math.round(((day.read_time || 0) / weekMaxReadTime) * 100)) + '%' }"></i>
            </div>
            <strong>{{ ['一', '二', '三', '四', '五', '六', '日'][index] }}</strong>
            <span>{{ day.date ? shortDate(day.date) : '' }}</span>
            <small>{{ heatmapDuration(day.read_time) }}</small>
          </div>
        </div>
      </div>
    </section>
  `,
};

const CategoryBars = {
  props: ["categories", "fallbackCover"],
  emits: ["select-book"],
  computed: {
  },
  template: `
    <div class="category-list">
      <button class="category-row" v-for="item in categories.slice(0, 9)" :key="item.category" type="button" @click="$emit('select-book', item.rep_book_id)">
        <img :src="item.rep_cover || fallbackCover" :alt="item.rep_title || item.category" loading="lazy" />
        <div class="category-row-text">
          <span>{{ item.category }}</span>
          <small>{{ item.rep_title || '暂无代表书籍' }}</small>
        </div>
      </button>
      <p class="empty-state" v-if="!categories.length">暂无分类数据</p>
    </div>
  `,
};

const DashboardPie = {
  props: ["categories"],
  computed: {
    colors() {
      return ["#0f766e", "#3b82f6", "#f97316", "#7c3aed", "#0ea5e9", "#e11d48", "#84cc16", "#f59e0b"];
    },
    total() {
      var t = this.categories.reduce(function(s, i) { return s + (Number(i.count) || 0); }, 0);
      return isNaN(t) ? 0 : t;
    },
    visibleTotal() {
      var t = this.categories.slice(0, 8).reduce(function(s, i) { return s + (Number(i.count) || 0); }, 0);
      return isNaN(t) ? 0 : t;
    },
    slices() {
      return this.categories.slice(0, 8).map((item, index) => ({
        category: item.category,
        count: item.count || 0,
        color: this.colors[index % this.colors.length],
        percent: this.total ? Math.round(((item.count || 0) / this.total) * 100) : 0,
      }));
    },
    topTags() {
      return this.slices.slice(0, 6);
    },
    pieStyle() {
      if (!this.slices.length || !this.visibleTotal) return { background: "#e5e7eb" };
      let cursor = 0;
      const stops = this.slices.map((item) => {
        const start = cursor;
        cursor += ((item.count || 0) / this.visibleTotal) * 100;
        return `${item.color} ${start}% ${cursor}%`;
      });
      return { background: `conic-gradient(${stops.join(", ")})` };
    },
  },
  template: `
    <section class="panel dashboard-pie-panel">
      <div class="panel-title">
        <div>
          <h3>分类分布</h3>
          <p>按藏书分类查看阅读结构</p>
        </div>
      </div>

      <div class="dashboard-pie">
        <div class="dashboard-pie-gauge" :style="pieStyle">
          <span class="dashboard-pie-core">
            <span>总藏书</span>
            <strong>{{ total }}</strong>
            <small>本</small>
          </span>
        </div>

        <div class="dashboard-pie-tags">
          <span class="pie-tag" v-for="item in topTags" :key="item.category">
            <i :style="{ background: item.color }"></i>
            {{ item.category }}
            <em>{{ item.percent || 0 }}%</em>
          </span>
        </div>
      </div>
    </section>
  `,
};

const CategoryPie = {
  props: ["categories"],
  computed: {
    colors() {
      return ["#0f766e", "#3b82f6", "#f97316", "#7c3aed", "#0ea5e9", "#e11d48", "#84cc16", "#f59e0b"];
    },
    total() {
      var t = this.categories.reduce(function(s, i) { return s + (Number(i.count) || 0); }, 0);
      return isNaN(t) ? 0 : t;
    },
    visibleTotal() {
      var t = this.categories.slice(0, 8).reduce(function(s, i) { return s + (Number(i.count) || 0); }, 0);
      return isNaN(t) ? 0 : t;
    },
    topCategory() {
      return this.slices[0] || { category: "暂无分类", count: 0, percent: 0, color: "#cbd5e1" };
    },
    otherCount() {
      return Math.max(0, this.total - this.visibleTotal);
    },
    otherPercent() {
      return this.total ? Math.round((this.otherCount / this.total) * 100) : 0;
    },
    slices() {
      return this.categories.slice(0, 8).map((item, index) => ({
        category: item.category,
        count: item.count || 0,
        color: this.colors[index % this.colors.length],
        percent: this.total ? Math.round(((item.count || 0) / this.total) * 100) : 0,
      }));
    },
    pieStyle() {
      if (!this.slices.length || !this.visibleTotal) return { background: "#e5e7eb" };
      let cursor = 0;
      const stops = this.slices.map((item) => {
        const start = cursor;
        cursor += ((item.count || 0) / this.visibleTotal) * 100;
        return `${item.color} ${start}% ${cursor}%`;
      });
      return { background: `conic-gradient(${stops.join(", ")})` };
    },
  },
  template: `
    <section class="panel category-dashboard-panel">
      <div class="panel-title">
        <div>
          <h3>分类分布仪表盘</h3>
          <p>按藏书分类查看阅读结构</p>
        </div>
        <span class="panel-count">{{ total || 0 }} 本</span>
      </div>

      <div class="category-dashboard">
        <div class="category-gauge-wrap">
          <div class="category-gauge" :style="pieStyle">
            <div class="category-gauge-core">
              <span>总藏书</span>
              <strong>{{ total || 0 }}</strong>
              <small>分类统计</small>
            </div>
          </div>
          <div class="category-top-card">
            <span>最大分类</span>
            <strong>{{ categories[0].category }}</strong>
            <small>{{ (categories[0] && categories[0].count) || 0 }} 本 · {{ topCategory.percent || 0 }}%</small>
            <p class="category-top-book" v-if="categories[0].rep_title">{{ categories[0].rep_title }}</p>
          </div>
        </div>

        <div class="category-rank">
          <div class="category-rank-item" v-for="item in slices" :key="item.category">
            <div class="category-rank-head">
              <span><i :style="{ background: item.color }"></i><em>{{ index + 1 }}</em> {{ item.category }}</span>
              <strong>{{ item.count || 0 }} 本</strong>
            </div>
            <div class="category-rank-bar">
              <i :style="{ width: Math.max(3, item.percent) + '%', background: item.color }"></i>
            </div>
            <small>{{ item.percent || 0 }}%</small>
          </div>

          <div class="category-rank-item muted" v-if="otherCount">
            <div class="category-rank-head">
              <span><i></i>其他分类</span>
              <strong>{{ otherCount || 0 }} 本</strong>
            </div>
            <div class="category-rank-bar">
              <i :style="{ width: Math.max(3, otherPercent) + '%' }"></i>
            </div>
            <small>{{ otherPercent || 0 }}%</small>
          </div>

          <p class="empty-state" v-if="!slices.length">暂无分类数据</p>
        </div>
      </div>
    </section>
  `,
};

const DashboardPage = {
  components: { MetricCard, ReadingStats, CurrentReading, ReadingHeatmap, DashboardPie },
  props: ["summary", "categories", "currentBooks", "heatmap", "fallbackCover"],
  emits: ["open-page", "select-book"],
  template: `
    <section class="page dashboard">
      <div class="metric-grid">
        <metric-card icon="library" label="藏书总数" :value="summary.counts.books" hint="来自同步数据库"></metric-card>
        <metric-card icon="timer" label="阅读时长" :value="summary.all_time_stats && summary.all_time_stats.total_read_time" format="hours" hint="全部阅读时间"></metric-card>
        <metric-card icon="calendar-days" label="阅读天数" :value="summary.all_time_stats && summary.all_time_stats.read_days" hint="有记录的阅读日"></metric-card>
        <metric-card icon="highlighter" label="个人划线" :value="summary.counts.bookmarks" hint="保存的标注内容"></metric-card>
        <metric-card icon="notebook" label="笔记想法" :value="summary.counts.reviews" hint="笔记和想法"></metric-card>
      </div>

      <div class="dashboard-grid">
        <reading-stats :summary="summary" @open-page="$emit('open-page', $event)"></reading-stats>
        <current-reading
          :items="currentBooks"
          :fallback-cover="fallbackCover"
          @select-book="$emit('select-book', $event)"
        ></current-reading>
      </div>

      <div class="visual-grid">
        <reading-heatmap :heatmap="heatmap"></reading-heatmap>
        <dashboard-pie :categories="categories"></dashboard-pie>
      </div>
    </section>
  `,
};

const CategoriesPage = {
  components: { CategoryBars, CategoryPie },
  props: ["categories", "summary"],
  props: ["categories", "summary", "fallbackCover"],
  emits: ["select-book"],
  methods: formatters,
  template: `
    <section class="page categories-view">
      <div class="section-head">
        <div>
          <h3>阅读地图</h3>
          <p>用分类分布观察阅读偏好和书架结构。</p>
        </div>
     </div>
      <div class="category-page-grid">
        <category-pie :categories="categories"></category-pie>
        <section class="panel">
          <div class="panel-title">
            <div>
              <h3>精品推荐</h3>
              <p>阅读时长由高到低</p>
            </div>
          </div>
         <category-bars :categories="categories" :fallback-cover="fallbackCover" @select-book="$emit('select-book', $event)"></category-bars>
        </section>
      </div>
    </section>
  `,
};

const NotesPage = {
  props: ["notes", "fallbackCover"],
 methods: {
   ...formatters,
   noteText(note) {
     return note.content || '空内容';
   },
   typeLabel(type) {
     return type === 'bookmark' ? '划线' : '想法';
   },
 },
 template: `
   <section class="page notes-view">
     <div class="section-head">
       <div>
         <h3>全部笔记</h3>
         <p>按时间整理你的划线和阅读想法。</p>
       </div>
       <strong>{{ notes.length }} 条</strong>
     </div>
     <div class="notes-grid">
       <article class="note" v-for="note in notes" :key="note.id + '_' + note.type">
         <div class="note-topline">
           <span :class="'type-' + note.type">{{ typeLabel(note.type) }}</span>
           <time>{{ date(note.create_time) }}</time>
         </div>
          <div class="note-book">
            <img :src="note.cover || fallbackCover" :alt="note.book_title || '封面'" loading="lazy" />
            <div>
              <h3>{{ note.book_title || '未归属书籍' }}</h3>
              <strong>{{ note.author || '未知作者' }}</strong>
              <span>{{ note.category || note.publisher || '未分类' }}</span>
              <div class="mini-progress" v-if="note.progress !== null && note.progress !== undefined">
                <i :style="{ width: percent(note.progress) }"></i>
              </div>
              <small v-if="note.progress !== null && note.progress !== undefined">{{ note.progress || 0 }}% · {{ duration(note.reading_time) }}</small>
            </div>
         </div>
         <blockquote v-if="note.type === 'note' && note.abstract_text">{{ note.abstract_text }}</blockquote>
         <p :class="{ 'thought-text': note.type === 'note' }">{{ noteText(note) }}</p>
         <div class="note-meta">
             <span>{{ note.chapter_name || note.author || '暂无章节' }}</span>
             <i v-if="note.type === 'note' && note.is_private">私密</i>
           </div>
         </article>
       </div>
       <p class="empty-state" v-if="!notes.length">暂无笔记数据</p>
     </section>
   `,
};

const BookDetailDrawer = {
  components: { Icon },
  props: ["detail", "fallbackCover"],
  emits: ["close"],
  data() {
    return { showFullIntro: false };
  },
  methods: formatters,
  computed: {
    ratingScore() {
      const r = this.detail.book.new_rating;
      return r ? (r / 100).toFixed(1) : '';
    },
    ratingTotal() {
      const b = this.detail.book;
      return (b.good || 0) + (b.fair || 0) + (b.poor || 0);
    },
    pubDate() {
      const d = this.detail.book.publish_time;
      if (!d) return '';
      const date = new Date(d);
      if (isNaN(date.getTime())) return d.substring(0, 10);
      return date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date.getDate()).padStart(2, '0');
    },
  },
  template: `
    <div class="detail-shell">
      <button class="detail-backdrop" type="button" aria-label="关闭详情" @click="$emit('close')"></button>
      <aside class="detail">
        <button class="close icon-button" type="button" title="关闭详情" @click="$emit('close')">
          <icon name="x"></icon>
        </button>
        <div class="detail-head">
          <img :src="detail.book.cover || fallbackCover" alt="封面" />
          <div>
            <h2>{{ detail.book.title }}</h2>
            <p class="detail-author">{{ detail.book.author }}</p>
            <p class="detail-sub" v-if="detail.book.translator || detail.book.publisher">
              {{ [detail.book.publisher, detail.book.translator ? '译者 ' + detail.book.translator : ''].filter(Boolean).join(' · ') }}
            </p>
          </div>
        </div>

        <div class="detail-rating-card" v-if="ratingScore || ratingTotal">
          <div class="rating-card-score">
            <icon name="star" :size="18"></icon>
            <strong>{{ ratingScore || '--' }}</strong>
            <span>/ 10</span>
          </div>
          <div class="rating-card-info" v-if="detail.book.rating_title || detail.book.new_rating_count">
            <span class="rating-card-title" v-if="detail.book.rating_title">{{ detail.book.rating_title }}</span>
            <span class="rating-card-count" v-if="detail.book.new_rating_count">{{ number(detail.book.new_rating_count) }} 人评分</span>
          </div>
          <div class="rating-card-dist" v-if="ratingTotal">
            <div class="rc-bar">
              <i class="good" :style="{ width: ratingGoodPct + '%' }"></i>
              <i class="fair" :style="{ width: ratingFairPct + '%' }"></i>
              <i class="poor" :style="{ width: ratingPoorPct + '%' }"></i>
            </div>
            <div class="rc-labels">
              <span><em class="rc-dot good-dot"></em>好评 {{ number(detail.book.good || 0) }}</span>
              <span><em class="rc-dot fair-dot"></em>一般 {{ number(detail.book.fair || 0) }}</span>
              <span><em class="rc-dot poor-dot"></em>差评 {{ number(detail.book.poor || 0) }}</span>
            </div>
          </div>
        </div>
        <div class="detail-progress">
          <div class="detail-progress-head">
            <span>阅读进度</span>
            <strong>{{ detail.book.progress || 0 }}%</strong>
          </div>
          <div class="detail-progress-bar">
            <i :style="{ width: percent(detail.book.progress) }"></i>
          </div>
        </div>
        <div class="detail-meta-grid">
          <div class="detail-meta-item">
            <icon name="folder-tree" :size="12"></icon>
            <span>{{ detail.book.category || '未分类' }}</span>
          </div>
          <div class="detail-meta-item" v-if="detail.book.isbn">
            <icon name="barcode" :size="12"></icon>
            <span>{{ detail.book.isbn }}</span>
          </div>
          <div class="detail-meta-item" v-if="detail.book.publish_time">
            <icon name="calendar" :size="12"></icon>
            <span>{{ pubDate }}</span>
          </div>
          <div class="detail-meta-item" v-if="detail.book.total_words > 0">
            <icon name="text" :size="12"></icon>
            <span>{{ number(detail.book.total_words) }} 字</span>
          </div>
          <div class="detail-meta-item" v-if="detail.book.new_rating_count">
            <icon name="users" :size="12"></icon>
            <span>{{ number(detail.book.new_rating_count) }} 人评分</span>
          </div>
          <div class="detail-meta-item" v-if="detail.book.finish_reading">
            <icon name="check-circle" :size="12"></icon>
            <span>已读完</span>
          </div>
        </div>
        <div class="intro-block" v-if="detail.book.intro">
          <div class="intro-label">简介</div>
          <p class="intro" :class="{ expanded: showFullIntro }">{{ detail.book.intro }}</p>
          <button class="intro-toggle" type="button" @click="showFullIntro = !showFullIntro">
            {{ showFullIntro ? '收起' : '查看全部' }}
          </button>
        </div>
        <section class="detail-section" v-if="detail.bookmarks.length">
          <h3><icon name="highlighter" :size="13"></icon> 划线</h3>
          <blockquote v-for="item in detail.bookmarks.slice(0, 1)" :key="item.bookmark_id">{{ item.mark_text }}</blockquote>
        </section>
        <section class="detail-section" v-if="detail.reviews.length">
          <h3><icon name="notebook-pen" :size="13"></icon> 笔记</h3>
          <blockquote v-for="item in detail.reviews.slice(0, 1)" :key="item.review_id">{{ item.content || item.abstract_text || '空笔记' }}</blockquote>
        </section>

        <p class="detail-empty" v-if="!detail.bookmarks.length && !detail.reviews.length">暂无个人划线和笔记</p>
      </aside>
    </div>
  `,
};



createApp({
  components: {
    AppSidebar,
    PageHeader,
    DashboardPie,
    DashboardPage,
    CategoriesPage,
    NotesPage,
    BookDetailDrawer,
  },
  data() {
    return {
      view: "dashboard",
     navItems: [
       { key: "dashboard", label: "总览", icon: "layout-dashboard" },
       { key: "categories", label: "分类", icon: "pie-chart" },
       { key: "notes", label: "划线", icon: "notebook-pen" },
     ],
      summary: { counts: {}, latest_stats: null, all_time_stats: {}, latest_sync: null },
      categories: [],
      currentBooks: [],
      heatmap: { months: [], max_read_time: 0, active_days: 0 },
      notes: [],
      selectedBook: null,
      error: "",
      fallbackCover:
        "data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='320' viewBox='0 0 240 320'%3E%3Crect width='240' height='320' rx='18' fill='%23eef2f5'/%3E%3Cpath d='M64 56h88a24 24 0 0 1 24 24v184H88a24 24 0 0 1-24-24V56Z' fill='%23ffffff' stroke='%23cbd5e1'/%3E%3Cpath d='M88 92h62M88 122h52M88 152h70' stroke='%2364758b' stroke-width='8' stroke-linecap='round'/%3E%3Ctext x='120' y='246' text-anchor='middle' font-size='22' fill='%230f766e' font-family='Arial'%3EWeRead%3C/text%3E%3C/svg%3E",
    };
  },
  computed: {
    title() {
     return {
       dashboard: "阅读总览",
       categories: "阅读分类",
       notes: "划线与想法",
     }[this.view];
   },
   subtitle() {
     return {
       dashboard: "快速查看藏书、阅读进度、笔记和热力图。",
       categories: "从书架分类里看见你的阅读版图。",
       notes: "你的划线标记和阅读想法。",
     }[this.view];
   },
  },
  watch: {
    view(next) {
      if (next === "notes" && !this.notes.length) this.loadNotes();
      iconTick();
    },
    selectedBook() {
      iconTick();
    },
  },
  mounted() {
    this.refreshData();
    iconTick();
  },
  updated: iconTick,
  methods: {
    setView(view) {
      this.view = view;
      this.selectedBook = null;
    },
    async api(url) {
      const response = await fetch(url, { cache: "no-store" });
      const payload = await response.json();
      if (!payload.ok) throw new Error(payload.error || "请求失败");
      return payload.data;
    },
    async refreshData() {
      this.error = "";
      try {
        const data = await this.api("/api/summary");
        this.summary = data;
      } catch (e) {
        this.error = "SUMMARY FAILED: " + e.message;
      }
      try {
        this.categories = await this.api("/api/categories");
      } catch (e) {}
      try {
        this.currentBooks = await this.api("/api/currently-reading");
      } catch (e) {}
      try {
        this.heatmap = await this.api("/api/reading-heatmap");
      } catch (e) {}
      if (this.view === "notes") await this.loadNotes();
      iconTick();
    },
    async loadSummary() {
      try {
        const data = await this.api("/api/summary");
        Object.assign(this.summary, data);
      } catch (error) {
        this.error = error.message;
      }
    },
    async loadCategories() {
      try {
        this.categories = await this.api("/api/categories");
      } catch (error) {
        this.error = error.message;
      }
    },
    async loadCurrentBooks() {
      try {
        this.currentBooks = await this.api("/api/currently-reading");
      } catch (error) {
        this.error = error.message;
      }
    },
    async loadHeatmap() {
      try {
        this.heatmap = await this.api("/api/reading-heatmap");
      } catch (error) {
        this.error = error.message;
      }
    },
    async loadNotes() {
      try {
        this.notes = await this.api("/api/recent-notes");
      } catch (error) {
        this.error = error.message;
      }
    },
    async selectBook(bookId) {
      try {
        this.selectedBook = await this.api(`/api/books/${bookId}`);
      } catch (error) {
        this.error = error.message;
      }
    },
  },
}).mount("#app");
