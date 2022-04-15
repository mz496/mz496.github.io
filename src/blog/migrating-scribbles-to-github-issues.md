---
title: Migrating scribbles to GitHub issues
description: The power of plaintext
date: 2022-01-21
tags:
  - post
  - records
---

I'm a small-time packrat when it comes to keeping data. Not [r/DataHoarder](https://reddit.com/r/datahoarder) level, but I recently moved lots of my "temporary" scribbles, half-baked ideas, and notes into what I decided is its safer yet still dynamic resting place: GitHub issues. Here's my reasoning.

These are all short-form bits like, "build a lamp that uses the principle of induction like \<Hackaday post I saw one time\>" or "make an Avalon/The Resistance clone for mobile." I call them "temporary" in thick quotation marks because my ideas were easy to jot down, telling myself I'd move them somewhere more permanent. But I never did, so they effectively became permanent, and the lists just kept proliferating.

Some of these places, starting around 2014-2015:
* **Google Keep.** I'm pretty sure I misused it by trying to consolidate everything into one list and failing. (That's what many small notes with tags are for.)
* **Tumblr.** I used to write journal entries there, so it was an easy choice. But I'd often forget to tag things and look back at them.
* **Trello.** Another one that enticed me with the illusion of organization but was a bit awkward to use for simple notes that only I look at.

Each of these, though, had a few things in common:
* **Mobile workflows were on par with desktop workflows.** I could just as easily write down an idea walking down the sidewalk as I could doing deep work.
* **Cloud sync was a given.** My brothers and I grew up with laptops that seemed to arrive new and slow to a crawl by the season -- granted, there were probably more powerful options, but this got me accustomed to mistrusting (my own, single-point-of-failure) hardware. Even those USB sticks that used to go for $20 a gig.
* **Ideas can be easily annotated and edited.** Each one is at its core a CRUD app.
* **Private space was free.** I mean at that time I could've been swayed by most things that were free so…

This all started when my oldest brother introduced me to [Org Mode](https://orgmode.org) for emacs. While I of course couldn't accept it on principle because it requires me to touch emacs (ง'̀-'́)ง, it got me thinking. What would get me to use Org Mode for notes? Similar to [Dropbox Paper](https://dropbox.com/paper), it's like text with superpowers: a sophisticated editor's rich syntax also falls back to normal text. So it's really like asking, what would it take for me to use *plain text* for notes?

A prerequisite would be how GitHub handles it. I'm already in the habit of managing my website through GitHub, so I investigated further. Turns out that specifically using GitHub issues meets all of those conditions, with a few extra goodies:
* **Great CLI (`gh`) for automation.** I got rate limited a few times, but hopefully this is the last time I need to create two hundred issues programmatically. Even their rate-limiting UI is nice, by the way.
* **A great search query language.** I don't anticipate needing to use it much, but it's front and center.
* **Simple delete and edit history.** I gazed briefly into the void of Trello's abstractions while trying to programmatically grab card contents during the migration and was not pleased.
* **Immutable timestamping,** instead of, say, last update time, which was useless when I had twenty ideas crammed in a single Keep note. Lineages are fun.

Now, after backfilling all those ideas, my workflow is: fire up the GitHub app, open my starred private repo, hit + to create an issue, type away, and that's it.

I've also written this post entirely on my phone, my elbows are sore, and the editor (only available on mobile web, not the app) doesn't soft wrap for me. So blogging from mobile… maybe not.
