---
title: Getting frequency data from sound files in JavaScript
description: A tiny example on how to use the Web Audio API
date: 2021-07-18
tags:
  - post
  - code
---

A few months ago, [Madeon's *The Prince* audio visualizer](https://www.youtube.com/watch?v=AOhFzDN3eMI) inspired me to create something fun with audio. A spectrogram or some kind of similar visualization maybe?

A lot of the tutorials I found took the approach "here's a full project I made and here's what my code looked like at every step." They were helpful to understand the potential of the Web Audio API, but I didn't want to recreate their project; I found myself searching for that one nugget of information "how did they extract the time frequency data?"

There's a huge wealth of cool applications out there, but I wish the guides would separate out core Web Audio API concepts before extending with other feature choices and technology choices like WebGL/canvas :| So I made the guide I wish I had!

All that said, I do think the [MDN docs](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) on the Web Audio API do a decent job of explaining in the first concepts and usage section.

Here's our plan:

## Setup bits
* Create things in the DOM to hold the result of the future visualization. (I've chosen to use a bunch of `div` elements nested in one large `div`. [L38-L45.](https://github.com/mz496/mz496.github.io/blob/6c5bdd5/js/spectrogram.js#L38-L45))
```html
<audio controls src="/files/spectrogram-input.mp3"></audio>
<div id="spectrogram">
  <div id="bin-0"></div>
  <div id="bin-1"></div>
  (programmatically generated...)
</div>
```

* On page load, get the input source. (I chose an `<audio>` element, although this could also be the [microphone](https://calebgannon.com/2021/01/09/spectrogram-with-three-js-and-glsl-shaders/) or the [audio stream from a `<video>` element.](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/createMediaStreamSource#example) [L37-L54.](https://github.com/mz496/mz496.github.io/blob/6c5bdd5/js/spectrogram.js#L37-L54))

## Web Audio API bits
* Create [AudioContext](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext). [L8-L9.](https://github.com/mz496/mz496.github.io/blob/6c5bdd5/js/spectrogram.js#L8-L9)
* Create an [AnalyserNode](https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode) effect. This is like a no-op effect, i.e. the output signal and input signal are the same. [L10-L12.](https://github.com/mz496/mz496.github.io/blob/6c5bdd5/js/spectrogram.js#L10-L12)
* Connect the sources to the effects, and the effects to the destination. [L13-L17.](https://github.com/mz496/mz496.github.io/blob/6c5bdd5/js/spectrogram.js#L13-L17)

## Processing bits
* On an interval, pull data out of the analyser node as an array of 8-bit numbers with `getByteFrequencyData`. [L21,](https://github.com/mz496/mz496.github.io/blob/6c5bdd5/js/spectrogram.js#L21) [L31.](https://github.com/mz496/mz496.github.io/blob/6c5bdd5/js/spectrogram.js#L31)
* Once you have the array, visualize it. (I've chosen to output a bunch of ASCII block-drawing characters █ according to the value in the array. [L22-L25.](https://github.com/mz496/mz496.github.io/blob/6c5bdd5/js/spectrogram.js#L22-L25))

## The result
<script src="/static/files/spectrogram.js"></script>

Audio input:

<audio controls src="/static/files/spectrogram-input.mp3"></audio>

<div id="spectrogram" style="font-family: monospace; font-size: 2pt; overflow-x: scroll"></div>

## Future work
There are a few issues with this:
* `setInterval` keeps running even when the sound is paused. That's wasting resources while the page is idle.
* The frequency axis (vertical here) is linear. But to match our perception, the scale should be logarithmic because we perceive frequencies separated by the same ratio as equally far apart, rather than frequencies separated by the same difference. ([This is the idea behind equal temperament.](https://en.wikipedia.org/wiki/Equal_temperament)) We could do this with more bins and subsampling logarithmically.

But these are immaterial to my goal here :)
