class SugarDocs {
    constructor() {
      this.data = null;
      this.currentSection = null;
      this.searchResults = [];
      this.activeTOCObserver = null;
      this.recentSearches = JSON.parse(localStorage.getItem('sugar_recent') || '[]').slice(0, 8);
      this.debouncers = new Map();
      this.init();
    }
  
    async init() {
      try {
        await this.loadData();
        this.cacheEls();
        this.bindGlobalUI();
        this.renderNavigation();
        this.handleFragmentNavigation();
        this.restoreTheme();
        this.installKeyboardShortcuts();
      } catch (e) {
        console.error('Initialization error:', e);
        this.showError(`Failed to load documentation data: ${e.message}`);
      }
    }
  
    cacheEls() {
      this.$ = (sel, root = document) => root.querySelector(sel);
      this.$$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
      this.content = this.$('#content');
      this.navSections = this.$('#nav-sections');
      this.navKeywords = this.$('#nav-keywords');
      this.navExamples = this.$('#nav-examples');
      this.sidebar = this.$('#sidebar');
      this.sidebarToggle = this.$('#sidebar-toggle');
      this.sidebarFilter = this.$('#sidebar-filter');
      this.searchBtn = this.$('#search-btn');
      this.searchDialog = this.$('#search-dialog');
      this.searchDialogInput = this.$('#search-dialog-input');
      this.searchDialogResults = this.$('#search-dialog-results');
      this.tocList = this.$('#toc-list');
    }
  
    async loadData() {
      const resp = await fetch('./sugar-language-reference.json', { cache: 'no-cache' });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      this.data = await resp.json();
    }
  
    bindGlobalUI() {
      // Sidebar toggle
      this.sidebarToggle.addEventListener('click', () => {
        const isMobile = window.matchMedia('(max-width:1024px)').matches;
        
        if (isMobile) {
          // Mobile behavior: toggle the .open class
          const open = !this.sidebar.classList.contains('open');
          this.sidebar.classList.toggle('open', open);
          this.sidebarToggle.setAttribute('aria-expanded', String(open));
        } else {
          // Desktop behavior: toggle the .collapsed class to hide/show sidebar
          const collapsed = !this.sidebar.classList.contains('collapsed');
          this.sidebar.classList.toggle('collapsed', collapsed);
          this.sidebarToggle.setAttribute('aria-expanded', String(!collapsed));
          
          // Also toggle the layout class to adjust the grid
          const layout = document.querySelector('.layout');
          layout.classList.toggle('sidebar-collapsed', collapsed);
        }
      });
      
      // Close sidebar when clicking outside on mobile
      document.addEventListener('click', (e) => {
        if (window.matchMedia('(max-width:1024px)').matches) {
          const isClickInsideSidebar = this.sidebar.contains(e.target);
          const isClickOnToggle = this.sidebarToggle.contains(e.target);
          
          if (!isClickInsideSidebar && !isClickOnToggle && this.sidebar.classList.contains('open')) {
            this.sidebar.classList.remove('open');
            this.sidebarToggle.setAttribute('aria-expanded', 'false');
          }
        }
      });
      
      // Touch/swipe to close sidebar on mobile
      let touchStartX = 0;
      let touchStartY = 0;
      
      document.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      });
      
      document.addEventListener('touchend', (e) => {
        if (!window.matchMedia('(max-width:1024px)').matches) return;
        if (!this.sidebar.classList.contains('open')) return;
        
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        const deltaX = touchStartX - touchEndX;
        const deltaY = Math.abs(touchStartY - touchEndY);
        
        // Swipe left to close (if swipe is horizontal and significant)
        if (deltaX > 50 && deltaY < 100 && touchStartX < 100) {
          this.sidebar.classList.remove('open');
          this.sidebarToggle.setAttribute('aria-expanded', 'false');
        }
      });
      
            this.$('#home-btn').addEventListener('click', (e) => { e.preventDefault(); this.showWelcome(); });

      // Handle window resize to sync sidebar state between mobile/desktop
      window.addEventListener('resize', () => {
        const isMobile = window.matchMedia('(max-width:1024px)').matches;
        const layout = document.querySelector('.layout');
        
        if (isMobile) {
          // On mobile, remove desktop-specific classes
          this.sidebar.classList.remove('collapsed');
          layout.classList.remove('sidebar-collapsed');
        } else {
          // On desktop, remove mobile-specific classes
          this.sidebar.classList.remove('open');
        }
      });

      // Collapsible sections in sidebar
      this.$$('.collapse-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const key = btn.dataset.collapse;
          const expanded = btn.getAttribute('aria-expanded') === 'true';
          btn.setAttribute('aria-expanded', String(!expanded));
          const ul = key === 'sections' ? this.navSections : key === 'keywords' ? this.navKeywords : this.navExamples;
          ul.style.display = expanded ? 'none' : '';
        });
      });
  
      // Sidebar keyword filter
      this.sidebarFilter.addEventListener('input', this.debounce((e) => {
        const q = e.target.value.trim().toLowerCase();
        this.$$(`#nav-keywords li`).forEach(li => {
          const t = li.textContent.toLowerCase();
          li.style.display = !q || t.includes(q) ? '' : 'none';
        });
      }, 120));
  
      // Search bar
  
      // Global search dialog
      this.$('#global-search-btn').addEventListener('click', () => this.openSearchDialog());
      this.searchDialog.addEventListener('close', () => this.searchDialogInput.value = '');
      this.searchDialogInput.addEventListener('input', this.debounce(() => this.renderGlobalSearch(this.searchDialogInput.value), 100));
      this.searchDialogResults.addEventListener('click', (e) => {
        const item = e.target.closest('.search-item');
        if (!item) return;
        this.navigateFromSearch(item.dataset.type, item.dataset.id);
        this.searchDialog.close();
      });
  
      // Deep-link navigation
      window.addEventListener('popstate', () => this.handleFragmentNavigation());
  
      // Code panel
      this.$('#close-code-panel').addEventListener('click', () => this.closeCodePanel());
  
      // Theme toggle
      this.$('#theme-toggle').addEventListener('click', () => this.toggleTheme());
    }
  
    installKeyboardShortcuts() {
      document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
          e.preventDefault();
          this.openSearchDialog();
        }
        
        // Close sidebar with Escape key on mobile
        if (e.key === 'Escape' && window.matchMedia('(max-width:1024px)').matches) {
          if (this.sidebar.classList.contains('open')) {
            e.preventDefault();
            this.sidebar.classList.remove('open');
            this.sidebarToggle.setAttribute('aria-expanded', 'false');
          }
        }
        
        if (this.searchDialog.open) {
          const items = this.$$('.search-item', this.searchDialogResults);
          const activeIndex = items.findIndex(i => i.getAttribute('aria-selected') === 'true');
          if (e.key === 'ArrowDown') {
            e.preventDefault();
            const next = Math.min(items.length - 1, activeIndex + 1);
            this.setActiveSearchItem(items, next);
          } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            const prev = Math.max(0, activeIndex - 1);
            this.setActiveSearchItem(items, prev);
          } else if (e.key === 'Enter') {
            const sel = items[activeIndex] || items[0];
            if (sel) {
              this.navigateFromSearch(sel.dataset.type, sel.dataset.id);
              this.searchDialog.close();
            }
          } else if (e.key === 'Escape') {
            this.searchDialog.close();
          }
        }
      });
    }
  
    openSearchDialog() {
      this.searchDialog.showModal();
      this.renderGlobalSearch(this.searchDialogInput.value);
      setTimeout(() => this.searchDialogInput.focus(), 0);
    }
  
    setActiveSearchItem(items, idx) {
      items.forEach(i => i.setAttribute('aria-selected', 'false'));
      if (items[idx]) {
        items[idx].setAttribute('aria-selected', 'true');
        items[idx].scrollIntoView({ block: 'nearest' });
      }
    }
  
    renderGlobalSearch(query) {
      const q = query.trim();
      let results = [];
      if (!q) {
        // Show recent
        results = this.recentSearches.map(r => ({ type: r.type, id: r.id, title: r.title, snippet: r.snippet || '' }));
      } else {
        results = this.fuzzySearch(q);
      }
      this.searchDialogResults.innerHTML = results.map((r, i) => `
        <div class="search-item" role="option" aria-selected="${i===0}" data-type="${r.type}" data-id="${r.id}">
          <div><strong>${this.escapeHtml(r.title)}</strong></div>
          ${r.snippet ? `<div class="muted">${this.escapeHtml(r.snippet)}</div>` : ''}
          <div class="muted" style="font-size:.8rem;margin-top:.2rem">${r.type}</div>
        </div>
      `).join('') || `<div class="search-item muted">No results</div>`;
    }
  
        fuzzySearch(query) {
      const q = query.toLowerCase();
      const max = 25;
      const results = [];

      // Debug: Check if data is loaded
      if (!this.data) {
        console.error('Search data not loaded');
        return [];
      }

      // Sections
      if (this.data.sections) {
        this.data.sections.forEach(s => {
          const text = JSON.stringify(s).toLowerCase();
          const score = this.score(text, q);
          if (score > 0) results.push({ type: 'section', id: s.id, title: s.title, score, snippet: (s.description || '').slice(0, 140) });
        });
      }

      // Keywords
      if (this.data.keywords) {
        Object.entries(this.data.keywords).forEach(([k, v]) => {
          const text = (k + ' ' + JSON.stringify(v)).toLowerCase();
          const score = this.score(text, q);
          if (score > 0) results.push({ type: 'keyword', id: k, title: k, score, snippet: (v.description || '').slice(0, 140) });
        });
      }

      // Examples
      if (this.data.examples && this.data.examples.complete) {
        this.data.examples.complete.forEach((ex, idx) => {
          const text = JSON.stringify(ex).toLowerCase();
          const score = this.score(text, q);
          if (score > 0) results.push({ type: 'example', id: idx, title: ex.title, score, snippet: ex.code.slice(0, 140) });
        });
      }

      results.sort((a, b) => b.score - a.score);
      return results.slice(0, max);
    }
  
    score(text, q) {
      // Simple fuzzy score: base matches plus weight for whole word matches
      if (!text.includes(q)) return 0;
      let s = 1;
      if (new RegExp(`\\b${this.escapeReg(q)}\\b`).test(text)) s += 1.5;
      s += Math.min(2, (text.match(new RegExp(this.escapeReg(q), 'g')) || []).length * 0.2);
      return s;
    }
  
    debounce(fn, ms = 150) {
      return (...args) => {
        const key = fn;
        clearTimeout(this.debouncers.get(key));
        const t = setTimeout(() => fn.apply(this, args), ms);
        this.debouncers.set(key, t);
      };
    }
  
    renderNavigation() {
      // Sections
      this.navSections.innerHTML = '';
      this.data.sections.forEach(s => {
        const li = document.createElement('li');
        li.innerHTML = `<a href="#section:${s.id}" data-section="${s.id}" role="treeitem">${s.title}</a>`;
        li.addEventListener('click', (e) => { e.preventDefault(); this.showSection(s.id); });
        this.navSections.appendChild(li);
      });
  
      // Keywords (virtualize if huge)
      this.navKeywords.innerHTML = '';
      Object.keys(this.data.keywords).sort().forEach(k => {
        const li = document.createElement('li');
        li.innerHTML = `<a href="#keyword:${k}" data-keyword="${k}" role="treeitem">${k}</a>`;
        li.addEventListener('click', (e) => { e.preventDefault(); this.showKeyword(k); });
        this.navKeywords.appendChild(li);
      });
  
      // Examples
      this.navExamples.innerHTML = '';
      this.data.examples.complete.forEach((ex, idx) => {
        const li = document.createElement('li');
        li.innerHTML = `<a href="#example:${idx}" data-example="${idx}" role="treeitem">${ex.title}</a>`;
        li.addEventListener('click', (e) => { e.preventDefault(); this.showExample(idx); });
        this.navExamples.appendChild(li);
      });
    }
  
    updateActiveNav(id, type) {
      this.$$('.nav-list a.active').forEach(a => a.classList.remove('active'));
      const link = this.$(`[data-${type}="${id}"]`);
      if (link) link.classList.add('active');
    }
  

  
    handleFragmentNavigation() {
      const hash = window.location.hash.slice(1);
      if (!hash) return this.showWelcome();
      const [type, id] = hash.split(':');
      if (type === 'section') return this.showSection(id);
      if (type === 'keyword') return this.showKeyword(id);
      if (type === 'example') return this.showExample(parseInt(id, 10));
      // Fallbacks
      if (this.data.sections.find(s => s.id === hash)) return this.showSection(hash);
      if (this.data.keywords[hash]) return this.showKeyword(hash);
      this.showWelcome();
    }
  
    updateURL(fragment) {
      if (history.pushState) history.pushState(null, '', fragment);
      else location.hash = fragment;
    }
  
    showWelcome() {
      this.updateURL('#');
      this.currentSection = null;
      this.updateActiveNav('', '');
  
      this.content.innerHTML = `
        <div class="section">
          <div class="section-header">
            <h1>Welcome to Sugar Language Documentation</h1>
            <button class="copy-link-btn" data-copy="#"
              title="Copy link to home">🔗</button>
          </div>
          <p>Sugar is a modern, expressive programming language with a clean syntax and powerful features. Use the sidebar to explore, or press Ctrl+/ to search.</p>
  
          <div class="examples-grid">
            ${this.welcomeCards()}
          </div>
        </div>
      `;
      this.bindCopyButtons();
      this.generateTOC();
      this.highlightCode();
    }
  
    welcomeCards() {
      return [
  `<div class="example-card">
    <h4>Basic Syntax</h4>
    <p>Variables, functions, and control flow.</p>
    <div class="code-block">
      <div class="code-actions">
        <button data-copy-code>Copy</button>
        <button class="code-preview-btn" data-code='DEF message #str = "Hello, Sugar!"
  DEF count #int = 42
  DEF is_valid #bool = :T:
  
  IO:PRINT:(message)
  IO:PRINT:(count)'>Preview</button>
      </div>
      <pre class="line-numbers"><code class="language-sugar">DEF message #str = "Hello, Sugar!"
  DEF count #int = 42
  DEF is_valid #bool = :T:
  
  IO:PRINT:(message)
  IO:PRINT:(count)</code></pre>
    </div>
  </div>`,
  `<div class="example-card">
    <h4>Object-Oriented Programming</h4>
    <p>Classes, inheritance, and interfaces.</p>
    <div class="code-block">
      <div class="code-actions">
        <button data-copy-code>Copy</button>
        <button class="code-preview-btn" data-code='CLASS Person
      PUBLIC name #str
      PUBLIC age #int
      
      PUBLIC CONSTRUCTOR(name #str, age #int) #void
          THIS.name := name
          THIS.age := age
      end
      
      PUBLIC FUNC greet() #str
          RETURN "Hello, " + THIS.name
      end
  end'>Preview</button>
      </div>
      <pre class="line-numbers"><code class="language-sugar">CLASS Person
      PUBLIC name #str
      PUBLIC age #int
      
      PUBLIC CONSTRUCTOR(name #str, age #int) #void
          THIS.name := name
          THIS.age := age
      end
      
      PUBLIC FUNC greet() #str
          RETURN "Hello, " + THIS.name
      end
  end</code></pre>
    </div>
  </div>`,
  `<div class="example-card">
    <h4>Pattern Matching</h4>
    <p>Powerful pattern matching capabilities.</p>
    <div class="code-block">
      <div class="code-actions">
        <button data-copy-code>Copy</button>
        <button class="code-preview-btn" data-code='MATCH value
      CASE #int x IF x > 0 DO
          IO:PRINT:("Positive integer")
      CASE #str s DO
          IO:PRINT:("String: " + s)
      DEFAULT DO
          IO:PRINT:("Unknown type")
  end'>Preview</button>
      </div>
      <pre class="line-numbers"><code class="language-sugar">MATCH value
      CASE #int x IF x > 0 DO
          IO:PRINT:("Positive integer")
      CASE #str s DO
          IO:PRINT:("String: " + s)
      DEFAULT DO
          IO:PRINT:("Unknown type")
  end</code></pre>
    </div>
  </div>`
      ].join('');
    }
  
    showSection(sectionId) {
      const section = this.data.sections.find(s => s.id === sectionId);
      if (!section) return;
  
      this.currentSection = section;
      this.updateActiveNav(sectionId, 'section');
      this.updateURL(`#section:${sectionId}`);
  
      let html = `
        <div class="section" id="${section.id}">
          <div class="section-header">
            <h1>${section.title}</h1>
            <button class="copy-link-btn" data-copy="#section:${sectionId}" title="Copy link to this section">🔗</button>
          </div>
          <p>${section?.description || ''}</p>
      `;
  
      if (section.subsections) html += section.subsections.map(s => this.renderSubsection(s)).join('');
      if (section.types) html += this.renderTypes(section.types);
      if (section.methods) html += this.renderMethods(section.methods);
      if (section.functions) html += this.renderFunctions(section.functions);
      if (section.constants) html += this.renderConstants(section.constants);
      if (section.examples) html += this.renderExamples(section.examples);
  
      html += '</div>';
  
      this.content.innerHTML = html;
      this.bindCopyButtons();
      this.bindCodeUtilities();
      this.generateTOC();
      this.highlightCode();
      this.maybeCloseSidebarOnMobile();
    }
  
    renderSubsection(subsection) {
      let html = `
        <section id="${subsection.id || this.slug(subsection.title)}" class="section">
          <h3>${subsection.title}</h3>
          ${subsection?.description ? `<p>${subsection.description}</p>` : ''}
      `;
  
      const listBlock = (arr) => `<ul>${arr.map(i => `<li>${i}</li>`).join('')}</ul>`;
      if (subsection.examples) html += this.renderExamples(subsection.examples);
      if (subsection.types) html += this.renderTypes(subsection.types);
      if (subsection.methods) html += this.renderMethods(subsection.methods);
      if (subsection.rules) html += listBlock(subsection.rules);
      if (subsection.features) html += listBlock(subsection.features);
      if (subsection.supported_iterables) html += listBlock(subsection.supported_iterables);
      if (subsection.pattern_types) html += listBlock(subsection.pattern_types);
  
      if (subsection.advanced_patterns) {
        html += '<div class="section"><h4>Advanced Patterns</h4>';
        html += subsection.advanced_patterns.map(p => `
          <div class="section">
            <h4>${p.type}</h4>
            <p>${p?.description || ''}</p>
            ${p.examples ? this.renderExamples(p.examples) : ''}
          </div>
        `).join('');
        html += '</div>';
      }
  
      if (subsection.patterns) {
        html += subsection.patterns.map(p => `
          <div class="section">
            <h4>${p.name}</h4>
            <p>${p?.description || ''}</p>
            <div class="code-block">
              <div class="code-actions">
                <button data-copy-code>Copy</button>
                <button class="code-preview-btn" data-code='${this.escapeAttr(p.example)}'>Preview</button>
              </div>
              <pre class="line-numbers"><code class="language-sugar">${this.escapeHtml(p.example)}</code></pre>
            </div>
          </div>
        `).join('');
      }
  
      html += '</section>';
      return html;
    }
  
    renderTypes(types) {
      return types.map(type => `
        <div class="section type-item" id="${this.slug('type-'+type.name)}">
          <h4><span class="inline-code">${type.name}</span></h4>
          <p>${type?.description || ''}</p>
          ${type.examples ? this.renderExamples(type.examples) : ''}
          ${type.literals ? `<p><strong>Literals:</strong> ${type.literals.map(l => `<code class="inline-code">${l}</code>`).join(', ')}</p>` : ''}
          ${type.usage ? `<p><strong>Usage:</strong> ${type.usage}</p>` : ''}
          ${type.properties ? `
            <table class="prop-table">
              <thead><tr><th>Name</th><th>Type</th><th>Description</th></tr></thead>
              <tbody>
                ${type.properties.map(p => `<tr><td><code class="inline-code">${p.name}</code></td><td>${p.type}</td><td>${p?.description || ''}</td></tr>`).join('')}
              </tbody>
            </table>` : ''}
        </div>
      `).join('');
    }
  
    renderMethods(methods) {
      return `
        <table class="method-table">
          <thead><tr><th>Method</th><th>Description</th><th>Examples</th></tr></thead>
          <tbody>
            ${methods.map(m => `
              <tr>
                <td><code class="inline-code">${m.name}</code></td>
                <td>${m?.description || ''}</td>
                <td>
                  ${(m.examples || []).map(ex => `
                    <div class="code-block">
                      <div class="code-actions">
                        <button data-copy-code>Copy</button>
                        <button class="code-preview-btn" data-code='${this.escapeAttr(ex)}'>Preview</button>
                      </div>
                      <pre class="line-numbers"><code class="language-sugar">${this.escapeHtml(ex)}</code></pre>
                    </div>`).join('')}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>`;
    }
  
    renderFunctions(functions) {
      return functions.map(f => `
        <div class="section function-item" id="${this.slug('fn-'+f.name)}">
          <h4><code class="inline-code">${f.name}</code></h4>
          <p>${f?.description || ''}</p>
          ${f.syntax ? `<p><strong>Syntax:</strong> <code class="inline-code">${f.syntax}</code></p>` : ''}
          ${f.examples ? this.renderExamples(f.examples) : ''}
        </div>
      `).join('');
    }
  
    renderConstants(constants) {
      return constants.map(c => `
        <div class="section constant-item" id="${this.slug('const-'+c.name)}">
          <h4><code class="inline-code">${c.name}</code></h4>
          <p>${c?.description || ''}</p>
          ${c.examples ? this.renderExamples(c.examples) : ''}
        </div>
      `).join('');
    }
  
    renderExamples(examples) {
      if (!Array.isArray(examples)) return '';
      return `
        <div class="examples-grid">
          ${examples.map(ex => `
            <div class="example-card">
              <div class="code-block">
                <div class="code-actions">
                  <button data-copy-code>Copy</button>
                  <button class="code-preview-btn" data-code='${this.escapeAttr(ex)}'>Preview</button>
                </div>
                <pre class="line-numbers"><code class="language-sugar">${this.escapeHtml(ex)}</code></pre>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }
  
    showKeyword(keyword) {
      const data = this.data.keywords[keyword];
      if (!data) return;
  
      this.currentSection = data;
      this.updateActiveNav(keyword, 'keyword');
      this.updateURL(`#keyword:${keyword}`);
  
      let html = `
        <div class="section" id="${this.slug('kw-'+keyword)}">
          <div class="section-header">
            <h1><span class="inline-code">${keyword}</span></h1>
            <button class="copy-link-btn" data-copy="#keyword:${keyword}" title="Copy link">🔗</button>
          </div>
          <p><strong>Category:</strong> ${data.category}</p>
          <p>${data?.description || ''}</p>
          ${data.syntax ? `<p><strong>Syntax:</strong> <code class="inline-code">${data.syntax}</code></p>` : ''}
          ${this.listSection('Rules', data.rules)}
          ${this.listSection('Features', data.features)}
          ${this.listSection('Supported Iterables', data.supported_iterables)}
          ${this.listSection('Pattern Types', data.pattern_types)}
      `;
  
      if (data.advanced_patterns) {
        html += '<h3>Advanced Patterns</h3>';
        html += data.advanced_patterns.map(p => `
          <div class="section">
            <h4>${p.type}</h4>
            <p>${p.description}</p>
            ${p.examples ? this.renderExamples(p.examples) : ''}
          </div>`).join('');
      }
  
      if (data.examples) {
        html += '<h3>Examples</h3>' + this.renderExamples(data.examples);
      }
  
      html += '</div>';
  
      this.content.innerHTML = html;
      this.bindCopyButtons();
      this.bindCodeUtilities();
      this.generateTOC();
      this.highlightCode();
      this.maybeCloseSidebarOnMobile();
    }
  
    listSection(title, list) {
      if (!list || !list.length) return '';
      return `<h3>${title}</h3><ul>${list.map(x => `<li>${x}</li>`).join('')}</ul>`;
    }
  
    showExample(idx) {
      const ex = this.data.examples.complete[idx];
      if (!ex) return;
  
      this.currentSection = ex;
      this.updateActiveNav(idx, 'example');
      this.updateURL(`#example:${idx}`);
  
      const html = `
        <div class="section" id="${this.slug('ex-'+ex.title)}">
          <div class="section-header">
            <h1>${ex.title}</h1>
            <button class="copy-link-btn" data-copy="#example:${idx}" title="Copy link">🔗</button>
          </div>
          <div class="code-block">
            <div class="code-actions">
              <button data-copy-code>Copy</button>
              <button class="code-preview-btn" data-code='${this.escapeAttr(ex.code)}'>Preview</button>
            </div>
            <pre class="line-numbers"><code class="language-sugar">${this.escapeHtml(ex.code)}</code></pre>
          </div>
        </div>
      `;
      this.content.innerHTML = html;
      this.bindCopyButtons();
      this.bindCodeUtilities();
      this.generateTOC();
      this.highlightCode();
      this.maybeCloseSidebarOnMobile();
  
      this.addRecent({ type: 'example', id: idx, title: ex.title, snippet: ex.code.slice(0, 120) });
    }
  
    addRecent(item) {
      this.recentSearches = [item, ...this.recentSearches.filter(i => i.type !== item.type || i.id !== item.id)].slice(0, 8);
      localStorage.setItem('sugar_recent', JSON.stringify(this.recentSearches));
    }
  
    navigateFromSearch(type, id) {
      if (type === 'section') this.showSection(id);
      else if (type === 'keyword') this.showKeyword(id);
      else if (type === 'example') this.showExample(parseInt(id, 10));
    }
  
    handleSearch(query) {
      const q = query.trim();
      if (!q) {
        this.content.innerHTML = `
          <div class="section"><h2>Search</h2><p>Type to search documentation.</p></div>
        `;
        return;
      }
      const results = this.fuzzySearch(q);
      const html = `
        <div class="section">
          <h2>Search Results (${results.length})</h2>
          <div class="search-results">
            ${results.map(r => `
              <div class="search-result" role="link" tabindex="0"
                data-type="${r.type}" data-id="${r.id}">
                <h4>${this.highlight(r.title, q)}</h4>
                <p>${this.highlight(r.snippet || '', q)}</p>
                <small class="muted">${r.type}</small>
              </div>`).join('')}
          </div>
        </div>
      `;
      this.content.innerHTML = html;
      this.$$('.search-result').forEach(el => {
        el.addEventListener('click', () => this.navigateFromSearch(el.dataset.type, el.dataset.id));
        el.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.navigateFromSearch(el.dataset.type, el.dataset.id); });
      });
      this.generateTOC(); // none, but keep consistent
    }
  
        generateTOC() {
      // Build from h2/h3/h4 in #content
      const heads = this.$$('#content h2, #content h3, #content h4');
      this.tocList.innerHTML = heads.map(h => {
        const id = h.id || (h.id = this.slug(h.textContent));
        return `<a href="#${id}" data-toc-id="${id}" style="margin-left:${h.tagName === 'H4' ? '1rem' : h.tagName === 'H3' ? '.5rem' : '0'}">${this.escapeHtml(h.textContent)}</a>`;
      }).join('');

      // Bind TOC link click events
      this.$$('#toc-list a').forEach(link => {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          const targetId = link.getAttribute('data-toc-id');
          const targetElement = this.$(`#${targetId}`);
          
          if (targetElement) {
            // Smooth scroll to the target element
            targetElement.scrollIntoView({ 
              behavior: 'smooth', 
              block: 'start' 
            });
            
            // Update URL without triggering navigation
            this.updateURL(`#${targetId}`);
          }
        });
      });

      // Scrollspy
      if (this.activeTOCObserver) this.activeTOCObserver.disconnect();
      const opts = { rootMargin: '0px 0px -70% 0px', threshold: 0 };
      this.activeTOCObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          const id = entry.target.id;
          const link = this.$(`[data-toc-id="${id}"]`);
          if (entry.isIntersecting) {
            this.$$('#toc-list a.active').forEach(a => a.classList.remove('active'));
            if (link) link.classList.add('active');
          }
        });
      }, opts);
      heads.forEach(h => this.activeTOCObserver.observe(h));
    }
  
    bindCopyButtons() {
      this.$$('#content .copy-link-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          const frag = btn.getAttribute('data-copy');
          const url = location.origin + location.pathname + frag;
          try {
            await navigator.clipboard.writeText(url);
            this.flash(btn, 'Copied');
          } catch {
            this.fallbackCopy(url);
            this.flash(btn, 'Copied');
          }
        });
      });
    }
  
    bindCodeUtilities() {
      // Copy code
      this.$$('#content [data-copy-code]').forEach(btn => {
        btn.addEventListener('click', async () => {
          const code = btn.closest('.code-block').querySelector('code').textContent;
          try {
            await navigator.clipboard.writeText(code);
            this.flash(btn, 'Copied');
          } catch {
            this.fallbackCopy(code);
            this.flash(btn, 'Copied');
          }
        });
      });
      // Preview
      this.$$('#content .code-preview-btn').forEach(btn => {
        btn.addEventListener('click', () => this.showCodePreview(btn.dataset.code));
      });
    }
  
    flash(el, text) {
      const original = el.textContent;
      el.textContent = text;
      el.disabled = true;
      setTimeout(() => { el.textContent = original; el.disabled = false; }, 1200);
    }
  
    fallbackCopy(text) {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
  
    showCodePreview(code) {
      const panel = this.$('#code-panel');
      const pre = this.$('#code-preview');
      pre.textContent = code;
      panel.classList.add('open');
      panel.setAttribute('aria-hidden', 'false');
      if (window.Prism) {
        pre.className = 'language-sugar';
        Prism.highlightElement(pre);
      }
    }
    closeCodePanel() {
      const panel = this.$('#code-panel');
      panel.classList.remove('open');
      panel.setAttribute('aria-hidden', 'true');
    }
  
    highlightCode() {
      // Re-run Prism efficiently
      if (!window.Prism || !Prism.languages.sugar) {
        setTimeout(() => this.highlightCode(), 150);
        return;
      }
      this.$$('#content pre code').forEach(block => {
        block.textContent = block.textContent; // normalize
        block.parentElement.classList.add('line-numbers');
        block.classList.add('language-sugar');
        Prism.highlightElement(block);
      });
    }
  
    maybeCloseSidebarOnMobile() {
      if (window.matchMedia('(max-width:1024px)').matches) {
        this.sidebar.classList.remove('open');
        this.sidebarToggle.setAttribute('aria-expanded', 'false');
      }
    }
  
    displaySearchResults() { /* replaced by handleSearch */ }
  
    showSearchResult(type, id) { this.navigateFromSearch(type, id); }
  
    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text ?? '';
      return div.innerHTML;
    }
    escapeAttr(text) {
      return (text ?? '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }
    slug(s) {
      return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    }
    escapeReg(s) {
      return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    highlight(text, query) {
      if (!query) return this.escapeHtml(text);
      const regex = new RegExp(`(${this.escapeReg(query)})`, 'gi');
      return this.escapeHtml(text).replace(regex, '<mark>$1</mark>');
    }
  
    toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'light' ? null : 'light';
      if (next) document.documentElement.setAttribute('data-theme', next);
      else document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('sugar_theme', next || 'dark');
    }
    restoreTheme() {
      const saved = localStorage.getItem('sugar_theme');
      if (saved === 'light') document.documentElement.setAttribute('data-theme', 'light');
    }
  
    showError(message) {
      this.content.innerHTML = `
        <div class="section">
          <h1>Error</h1>
          <p>${this.escapeHtml(message)}</p>
        </div>
      `;
    }
  }
  
  // Init
  const sugarDocs = new SugarDocs();
  window.showSearchResult = (type, id) => sugarDocs.showSearchResult(type, id);
  window.copyLink = (fragment) => navigator.clipboard.writeText(location.origin + location.pathname + fragment);