AUTHOR = 'r98inver'
SITENAME = "r98inver's blog"
SITEURL = ''

PATH = 'content'

TIMEZONE = 'UTC'

DEFAULT_LANG = 'en'

# THEME SETTINGS
THEME = 'themes/blue-penguin-dark'

# all defaults to True.
DISPLAY_HEADER = True
DISPLAY_FOOTER = True
DISPLAY_HOME   = True
DISPLAY_MENU   = True
DARK_LIGHT_SWITCHING_OFF = True

# provided as examples, they make ‘clean’ urls. used by MENU_INTERNAL_PAGES.
TAGS_URL           = 'tags'
TAGS_SAVE_AS       = 'tags/index.html'
AUTHORS_URL        = 'authors'
AUTHORS_SAVE_AS    = 'authors/index.html'
CATEGORIES_URL     = 'categories'
CATEGORIES_SAVE_AS = 'categories/index.html'
ARCHIVES_URL       = 'archives'
ARCHIVES_SAVE_AS   = 'archives/index.html'

# Pages and Articles
ARTICLE_URL = 'writeups/{slug}.html'
ARTICLE_SAVE_AS = 'writeups/{slug}.html'

# Other option
# ARTICLE_URL = 'writeups/{slug}/'
# ARTICLE_SAVE_AS = 'writeups/{slug}/index.html'

PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'

DIRECT_TEMPLATES = ['index', 'authors', 'categories', 'tags', 'archives']
TEMPLATE_PAGES = {
    'writeups.html': 'writeups/index.html'
}

STATIC_PATHS = ['images', 'pdfs'] # Adding cv

MENU_INTERNAL_PAGES = (
    ('CTF Writeups', 'writeups', 'writeups/index.html'),
    )
# use those if you want pelican standard pages to appear in your menu
# MENU_INTERNAL_PAGES = (
#     ('Categories', CATEGORIES_URL, CATEGORIES_SAVE_AS),
#     ('Tags', TAGS_URL, TAGS_SAVE_AS),
# )

# additional menu items
# MENUITEMS = (
#     ('GitHub', 'https://github.com/'),
#     ('Linux Kernel', 'https://www.kernel.org/'),
# )

# example pagination pattern
PAGINATION_PATTERNS = (
    (1, '{url}', '{save_as}'),
    (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
)




# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#           ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Custom settings
DISPLAY_CATEGORIES_ON_MENU = False 
SUMMARY_MAX_LENGTH = 50 # For summary created from page