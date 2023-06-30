---
title: Installing TidalCycles on Mac with Vim
description: An extremely bare-bones guide from end-to-end on installing TidalCycles on an M1 Mac
date: 2023-06-29
tags:
  - post
  - music
---

So you want to make live music with computers while feeling like a 1337 hacker?

This is an extremely bare-bones guide to installing TidalCycles on an M1 Mac with vim. This is mostly for myself and so assumes a lot of familiarity around a terminal. It's probably best suited for software engineers as is.

- Install TidalCycles: [MacOS instructions here](http://tidalcycles.org/docs/getting-started/macos_install) will lead to this [GitHub repo](https://github.com/tidalcycles/tidal-bootstrap)
    - This also installs [SuperCollider](https://supercollider.github.io/) and importantly, `sclang`, the interpreter
    - Brief background/reminder: TidalCycles is the pattern language, SuperCollider is the special sound generation language/IDE, SuperDirt is the sound generator
- Override the `sclang` startup script to make sure SuperDirt starts up at the same time as the interpreter: location from the [SuperCollider Startup File doc](https://doc.sccode.org/Reference/StartupFile.html) and script in the [SuperDirt repo](https://github.com/musikinformatik/SuperDirt/blob/develop/superdirt_startup.scd), which is referenced from the [TidalCycles Custom Samples doc](http://tidalcycles.org/docs/configuration/AudioSamples/audiosamples/)
- Alias sclang for convenience in `~/.zshrc`: add line `alias sclang="/Applications/SuperCollider.app/Contents/MacOS/sclang"` (h/t [The Leo Zone, retrieved 2023-06-29](https://theleo.zone/posts/tidal-cycles-setup/))
- Checkpoint: try `sclang` from terminal to make sure it works and prints out some SuperDirt stuff
- Install [vim-tidal](https://github.com/tidalcycles/vim-tidal) using plugin manager/installation method of choice
    - Install tmux if not already installed, a prerequisite here (but you'll run into this later when tmux isn't found anyway)
- Clone vim-tidal locally as well and run `make` from the repo root to establish symlinks
- Create a [tmuxinator](https://github.com/tmuxinator/tmuxinator) project to start up `vim`, `sclang`, `tidal` all at once:
    - `tmuxinator new music`
    - Paste this config. Notes:
        - `~/ANY-PATH` is where the tmux sessions will start, so if you end up saving the file, it will go here
        - `x.tidal` has a `.tidal` extension is so that vim properly interprets the file as a tidal file, which apparently lets you use the tidal-specific shortcuts (at least, they don't work without the extension)
        ```
        name: music
        socket_name: music_socket
        root: ~/ANY-PATH

        windows:
          - editor:
              panes:
                - vim x.tidal
          - server:
              panes:
                - sclang
                - tidal
        ```
        - If not already, `let maplocalleader=","` is convenient in `~/.vimrc`, else the default is `\`
        - Add to `~/.vimrc`, which tells vim-tidal to send input to the 1st window (server) and 1st pane (tidal)
        ```
        let g:tidal_target="tmux"
        let g:tidal_default_config = {"socket_name": "music_socket", "target_pane": "music:1.1"}
        ```
- `tmuxinator start music` to start
- In the `editor` window, try a basic command like `d1 $ sound "bd sd"` and type `<localleader>ss` in normal mode while on that line. Sound should be playing now. If not, check the `server` window for any errors
- To quit, `:q!` and `tmuxinator stop music`

