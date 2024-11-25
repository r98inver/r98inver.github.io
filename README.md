# My blog

Forked from [no-style-please](https://github.com/riggraz/no-style-please)

## Installation

- install dependencies: `sudo apt install ruby-dev ruby-bundler`
- create writable dir: `mkdir ~/.bundle_install`
- `bundle install`
- `bundle exec jekyll s`

## Quick usage

- To add a paper/preprint/talk: go to `_data` and modify the corresponding `yml` file
- Save pdf or other files in the corresponding directory

## Features

* Fast (**1kb of CSS!** For more information on performance and more, see [Page Speed Insights report](https://raw.githubusercontent.com/riggraz/no-style-please/master/_screenshots/page-speed-insights-report.png) and [Lighthouse report](https://raw.githubusercontent.com/riggraz/no-style-please/master/_screenshots/lighthouse-report.png))
* Light, dark and auto modes
* Responsive
* Content first (typography optimized for maximum readability)
* SEO optimized (uses [Jekyll SEO Tag](https://github.com/jekyll/jekyll-seo-tag))
* RSS feed (uses [Jekyll Feed](https://github.com/jekyll/jekyll-feed))
* Fully compatible with [GitHub Pages](https://pages.github.com/) (see [GitHub Pages installation](#github-pages-installation))

## Usage

### Website configuration

- Main cofiguration: `_config.yml`

### Main menu

- the page is `index.md`, and uses layout `home` which displays the menu; content in `index.md` is displayed under the menu
- `theme_config.show_description: true` in `_config.yml` shows the description of the blog
- the layout renders `_data/menu.yml`
- which in turns includes `_includes/menu_item` that unrolls the list

In order to add/edit/delete entries from the main menu, you have to edit the `menu.yml` file inside `_data` folder. Through that file you can define the structure of the menu. Take a look at the default configuration to get an idea of how it works and read on for a more comprehensive explanation.

The `_data/menu.yml` file accepts the following fields:

- `entries` define a new unordered list that will contain menu entries
- each entry is marked by a `-` at the beginning of the line
- each entry can have the following attributes:
    - `title`, which defines the text to render for this menu entry (**NB: you can also specify HTML!**)
    - `url`, which can be used to specify an URL for this entry. If not specified, `title` will be rendered as-is; otherwise `title` will be sorrounded by a link tag pointing to the specified URL. Note that the URL can either be relative or absolute. Also note that you can get the same result by placing an ```<a>``` tag in the `title` field.
    - `post_list`, which can be set either to `true` or to an object. If it is true, the entry will have a list of all posts as subentries. This is used to render your post list. If you want to customize which posts to render (e.g. by category), you can add one or more of the following attributes under `post_list`:
        - `category`, which can be set to a string. It is used to render a list of posts of the specified category only. If you don't set it, then posts of all categories will be rendered.
        - `limit`, which can be set to a number. It specifies the number of posts to show. If not set, all posts will be rendered.
        - `show_more`, which can be true. If it is true and if the number of posts to show is greater than the specified `limit`, render a link to another page. To specify the URL and the text of the link, you can set `show_more_url` and `show_more_text` attributes, which are documented below.
        - `show_more_url`, which can be a string. It specifies the URL for the show more link. Use only if `show_more` is true. This will usually redirect to a page containing all posts, which you can easily create using an archive page (see [create archive pages](#create-archive-pages) section)
        - `show_more_text`, which can be a string. It specifies the text for the show more link. Use only if `show_more` is true.
    - `entries`, yes, you can have entries inside entries. In this way you can create nested sublists!

Snippet:

```
  - title: all posts
    post_list:
      limit: 5
      show_more: true
      show_more_text: See archive...
      show_more_url: archive.html

  - title: posts by category
    post_list:
      category: example2
      show_more: true
      show_more_text: See more posts...
      show_more_url: example2-archive.html

  - title: rss
    url: feed.xml
```

### Create normal pages

- Pages are in `_pages/x.md` and are rendered in `/x`
- To make lists: add them in `_data/list.yml` and include `_includes/menu_item.html`

### Create archive pages

A so-called archive page is a page that shows a list of posts (see [this](https://riggraz.dev/no-style-please/all-posts) for an example). You can create an archive page by creating a page and putting the following frontmatter:

```
---
layout: archive
title: The title of the page here
which_category: name-of-category
---
```

`which_category` is optional: if you don't put it, then all posts of the blog will be listed; on the other hand, if you specify a category, only posts of that category will be shown.

This feature is particularly useful if used together with the `show_more` attribute in the menu. For example, if you want to limit the number of posts shown in the home page to 5 but add a link to view them all, then you can create an archive page using the method showed above and link to it using the `show_more_url` attribute in `menu.yml`. See [this example](https://github.com/riggraz/no-style-please/blob/master/_data/menu.yml) if you're in doubt.



## License

The theme is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

