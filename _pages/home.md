---
title: "Home"
layout: homelay
excerpt: "RT2 Lab at Institut Curie"
sitemap: false
permalink: /
---

### About the Lab

<p>
  WSSL's broad research interests are in the areas of AI-powered mobile/wearable computing and sustainable computing. Our research agenda
  has focused on <b>Sustainable Autonomous Things (SATs) </b> for the vision of the
  <b>Internet of Sustainable Medical Things, Internet of Sustainable Living Things</b>, and <b>Internet of Sustainable Flying Things</b>.
  Our work is interdisciplinary in nature, where we develop new techniques in sensor and sensing system development, algorithms, data
  analytics, signal processing, hardware, and firmware optimization to invent:
</p>

<ul>
  <li>
    (1) a new class of <b>medical devices</b> that can continuously and unobtrusively collect novel and important health data in
    non-clinical settings
  </li>
  <li>(2) a new class of <b>living sensors</b> that can live with plants/animals</li>
  <li>(3) a new class of <b>unmanned aerial vehicles</b> that requires extremely low maintenance.</li>
  <li>(4) We are also interested in <b>sustainable quantum computing</b>, and with Berkeley Lab, we have made some exciting progress.</li>
</ul>

### News

<ul class="list-unstyled">
  {% for article in site.data.news %}
  <li class="media">
    <div class="media-body">
      <!-- <h4 class="mt-0 mb-1">{{ article.title }}</h4> -->
      <!-- <p><small>{{ article.date }}</small></p> -->
	  {{ article.date }}:
      {% assign updated_content = article.content %} 
      {% for highlight in article.highlights %}
      {% if updated_content contains highlight.content %}
	       {% if highlight.url contains "https://" or highlight.url contains "http://" %}
	            {% assign highlight_with_link = "<a href='" | append: highlight.url | append: "' target='_blank'><b>" | append: highlight.content | append: "</b></a>" %}
	       {% else %}
	            {% assign highlight_with_link = "<b>" | append: highlight.content | append: "</b>" %}
	       {% endif %}
	       {% assign updated_content = updated_content | replace: highlight.content, highlight_with_link %}
      {% endif %}
      {% endfor %}

      <!-- {{ updated_content }} -->
	  {{updated_content}}
    </div>
  </li>
  {% endfor %}
</ul>


### Research Sponsors

<p>
  We are grateful for the support provided by our research sponsors. Their contributions enable us to continue innovating in our fields of
  expertise.
</p>

<div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; text-align: center;">
  <img src="{{ site.baseurl }}/images/sponsors/dolby.png" alt="dolby Logo" style="width: 100px; height: auto; margin: 10px;" />
  <img src="{{ site.baseurl }}/images/sponsors/IALS.png" alt="IALS Logo" style="width: 100px; height: auto; margin: 10px;" />
  <img src="{{ site.baseurl }}/images/sponsors/UMASS.png" alt="UMASS Logo" style="width: 100px; height: auto; margin: 10px;" />
  <img src="{{ site.baseurl }}/images/sponsors/UofTsystem_seal.svg" alt="UofT System Seal" style="width: 100px; height: auto; margin: 10px;" />
  <img src="{{ site.baseurl }}/images/sponsors/cics.jpg" alt="CICS Logo" style="width: 100px; height: auto; margin: 10px;" />
  <img src="{{ site.baseurl }}/images/sponsors/nih_nia.png" alt="NIH NIA Logo" style="width: 100px; height: auto; margin: 10px;" />
  <img src="{{ site.baseurl }}/images/sponsors/nsf.png" alt="NSF Logo" style="width: 100px; height: auto; margin: 10px;" />
  <img src="{{ site.baseurl }}/images/sponsors/sony.png" alt="Sony Logo" style="width: 100px; height: auto; margin: 10px;" />
</div>