---
layout: page
title: research
---

{% if site.data.preprints %}

## preprints

{% include papers_list.html collection=site.data.preprints.entries %}

{% endif %}

## papers

{% include papers_list.html collection=site.data.papers.entries %}

## talks

{% include talks_list.html collection=site.data.talks.entries %}
