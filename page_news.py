"""Miami Real Estate News – latest commercial & residential news from multiple sources."""
import streamlit as st
import datetime


def _fetch_news():
    """Fetch Miami real estate news from RSS feeds and web sources."""
    import urllib.request
    import xml.etree.ElementTree as ET

    feeds = [
        {
            "name": "The Real Deal - South Florida",
            "url": "https://therealdeal.com/miami/feed/",
            "source": "The Real Deal",
            "category": "Commercial & Residential",
        },
        {
            "name": "South Florida Business Journal - Real Estate",
            "url": "https://feeds.bizjournals.com/bizj_southflorida?format=xml",
            "source": "SFBJ",
            "category": "Commercial",
        },
        {
            "name": "Miami Herald - Real Estate",
            "url": "https://www.miamiherald.com/news/business/real-estate-news/?widgetName=rssfeed&widgetContentId=712015&get498tele498498Content=getRss&modelName=widget",
            "source": "Miami Herald",
            "category": "Residential & Commercial",
        },
        {
            "name": "GlobeSt - Southeast",
            "url": "https://www.globest.com/feed/",
            "source": "GlobeSt",
            "category": "Commercial",
        },
        {
            "name": "Commercial Observer - South Florida",
            "url": "https://commercialobserver.com/feed/",
            "source": "Commercial Observer",
            "category": "Commercial",
        },
    ]

    all_articles = []
    for feed in feeds:
        try:
            req = urllib.request.Request(feed["url"], headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            })
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
            root = ET.fromstring(data)
            # RSS 2.0 format
            items = root.findall(".//item")
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

            for item in items[:10]:
                title = _get_text(item, "title") or _get_text(item, "{http://www.w3.org/2005/Atom}title")
                link = _get_text(item, "link") or ""
                if not link:
                    link_el = item.find("{http://www.w3.org/2005/Atom}link")
                    if link_el is not None:
                        link = link_el.get("href", "")
                desc = _get_text(item, "description") or _get_text(item, "{http://www.w3.org/2005/Atom}summary") or ""
                pub_date = _get_text(item, "pubDate") or _get_text(item, "{http://www.w3.org/2005/Atom}published") or ""

                if not title:
                    continue

                # Filter for Miami/South Florida relevance
                text_check = (title + " " + desc).lower()
                miami_relevant = any(kw in text_check for kw in [
                    "miami", "dade", "brickell", "coral gables", "doral",
                    "south florida", "broward", "fort lauderdale", "palm beach",
                    "wynwood", "downtown miami", "coconut grove", "aventura",
                    "hialeah", "kendall", "homestead", "key biscayne",
                    "office", "retail", "industrial", "multifamily", "condo",
                    "commercial", "residential", "lease", "development",
                    "real estate", "property", "building",
                ])
                if not miami_relevant and "miami" not in feed["name"].lower():
                    continue

                # Clean description (remove HTML tags)
                import re
                clean_desc = re.sub(r'<[^>]+>', '', desc)[:300]

                all_articles.append({
                    "title": title.strip(),
                    "link": link.strip(),
                    "description": clean_desc.strip(),
                    "date": pub_date.strip(),
                    "source": feed["source"],
                    "category": feed["category"],
                })
        except Exception:
            continue

    # Sort by date (newest first) — best effort
    return all_articles


def _get_text(el, tag):
    """Get text content from XML element."""
    child = el.find(tag)
    if child is not None and child.text:
        return child.text
    return ""


def render_news_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="news_back"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Miami Real Estate News</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Latest commercial &amp; residential real estate news &mdash; South Florida</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    # Filters
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        cat_filter = st.selectbox("Category", ["All", "Commercial", "Residential"], key="news_cat")
    with filter_col2:
        search = st.text_input("Search", placeholder="Search articles...", key="news_search")

    with st.spinner("Loading latest news..."):
        articles = _fetch_news()

    if not articles:
        st.markdown(
            '<div class="card" style="text-align:center;padding:3rem;">'
            '<div style="font-size:2.5rem;margin-bottom:1rem;">&#128240;</div>'
            '<div style="font-size:1rem;font-weight:600;color:var(--text-primary);">Unable to load news</div>'
            '<div style="font-size:0.82rem;color:var(--text-tertiary);margin-top:0.5rem;">Check your internet connection and try again.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    # Apply filters
    filtered = articles
    if cat_filter != "All":
        filtered = [a for a in filtered if cat_filter.lower() in a["category"].lower()]
    if search:
        q = search.lower()
        filtered = [a for a in filtered if q in a["title"].lower() or q in a["description"].lower()]

    # KPIs
    sources = set(a["source"] for a in filtered)
    st.markdown(
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem;">'
        '<div class="kpi-card"><div class="kl">Articles</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Sources</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Updated</div><div class="kv">{}</div></div>'
        '</div>'.format(len(filtered), len(sources), datetime.datetime.now().strftime("%H:%M")),
        unsafe_allow_html=True,
    )

    # Display articles
    for a in filtered:
        source_badge = '<span class="badge badge-blue">{}</span>'.format(a["source"])
        cat_parts = a["category"].split(" & ")
        cat_badges = ""
        for cp in cat_parts:
            cp = cp.strip()
            badge_cls = "badge-green" if "Commercial" in cp else "badge-amber"
            cat_badges += ' <span class="badge {}">{}</span>'.format(badge_cls, cp)

        date_str = ""
        if a["date"]:
            date_str = '<span style="font-size:0.65rem;color:var(--text-muted);margin-left:0.5rem;">{}</span>'.format(a["date"][:25])

        link_html = ""
        if a["link"]:
            link_html = '<a href="{}" target="_blank" style="font-size:0.75rem;color:var(--accent);text-decoration:none;font-weight:600;">Read full article &rarr;</a>'.format(a["link"])

        st.markdown(
            '<div class="card" style="padding:1.2rem 1.5rem;">'
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">'
            '<div style="font-size:0.95rem;font-weight:700;color:var(--text-primary);line-height:1.4;flex:1;">{title}</div>'
            '</div>'
            '<div style="display:flex;gap:0.4rem;align-items:center;margin-bottom:0.6rem;flex-wrap:wrap;">'
            '{source}{cats}{date}'
            '</div>'
            '<p style="font-size:0.8rem;color:var(--text-secondary);line-height:1.6;margin:0 0 0.6rem;">{desc}</p>'
            '{link}'
            '</div>'.format(
                title=a["title"], source=source_badge, cats=cat_badges,
                date=date_str, desc=a["description"], link=link_html,
            ),
            unsafe_allow_html=True,
        )

    # Sources footer
    st.markdown(
        '<div style="text-align:center;margin-top:2rem;padding:1rem;">'
        '<div style="font-size:0.6rem;color:var(--text-muted);letter-spacing:0.5px;">'
        'Sources: The Real Deal, South Florida Business Journal, Miami Herald, GlobeSt, Commercial Observer</div>'
        '</div>',
        unsafe_allow_html=True,
    )
