---
title: Mario never dies
description: I gave Mario a multiverse. Every death branches into four timelines, and only the one that survives becomes canon.
cover: stephen
cover_art: mario-never-dies
tags: [microsandbox, snapshots, games]
---
Last week I built a version of Super Mario Bros where Mario can't really die. The game runs inside a VM that I can freeze and copy at any moment, and Jev, a System One model from TypeSafe AI, is the one playing. When Mario dies, the VM winds back a couple of seconds and splits into four copies, each one trying something different. Whichever one survives becomes the game from then on. It's called [Mario Never Dies](https://github.com/superradcompany/mario-never-dies), and it started the way a lot of my projects start, with me scrolling X and seeing something I had to try myself.

{% include video.html url="https://www.youtube.com/watch?v=92_MfHGNHEw" poster="/assets/posts/mario-never-dies/video-poster.png" alt="Four labeled copies of Mario running the same moment" title="watch it run" meta="2 min on youtube · four Marios, one survives" %}

## the itch

When [Diogo Almeida announced Jev](https://x.com/CompleteSkeptic/status/2099925682726002904), my timeline blew up. The launch post got tens of millions of views in a few days. Then the demos started. People had Jev [driving a browser](https://x.com/gregpr07/status/2100411066966749359), [using a desktop](https://x.com/milindlabs/status/2100631847155994852) and [playing Flappy Bird](https://x.com/anshnanda/status/2100611596859093082), and [they kept coming all week](https://x.com/moritzkremb/status/2100895894287839255).

If your timeline was better curated than mine, Jev is a different kind of model from the ones you chat with. It doesn't write any text. You send it a description of what's going on, along with a question that has a fixed set of answers, and it sends back its pick.

I bookmarked a bunch of those demos and knew I wanted to build something with Jev too. I just hadn't figured out what.

Around the same time, we shipped version 0.7 of [microsandbox](https://github.com/superradcompany/microsandbox), which is what I work on. It runs lightweight Linux VMs, mostly so AI agents have somewhere safe to run things. The big additions in 0.7 were full memory snapshots, pause and resume, and branching. Basically, you can freeze a running VM with everything in it, then start as many copies of that frozen moment as you want. Each copy carries on like nothing happened. It's hard to show off, though, because in a terminal all you see is a line saying a branch took 160ms.

So I wanted a demo that used both. I had seen a lot of game demos by then, and Mario is where it clicked. If you've played games, you know what it's like to die and lose twenty minutes of progress. What about a game where the main character never dies? I was calling it "Mario never dies" before there was any code.

## how it works

jev can only answer with one of the moves i hand it. no text out the other end.
{:.aside}

I didn't start from zero. Faadil Shaik had already built [typesafe-mario](https://github.com/fhshaik/typesafe-mario), which gets Jev playing Super Mario Bros in an NES emulator. Jev doesn't get to see the screen. The code reads the emulator's memory and turns it into a summary of the situation, like where Mario is, how fast he's moving, and whether there's an enemy or a gap coming up. Every 8 frames, Jev gets that summary and answers with which buttons to hold for the next 8.


My part was putting all of that inside a microsandbox VM and adding the bit that brings Mario back. Roughly every two and a half seconds of game time, microsandbox freezes a copy of the VM while the original keeps playing. If you've ever used save states in an emulator, it's the same idea, except the thing being saved is the entire computer. The emulator, the Python program driving it, the memory and the disk all get frozen together.

When Mario dies, the VM he died in gets thrown away. A copy from a couple of seconds earlier gets branched into four running VMs at once, each one nudged into a different opening move. For a moment you're watching four Marios walk up to the same Goomba. The first one to get past it alive becomes the real run. The other three get shut down, even the ones that were still doing fine.


early on the copies only differed for their first 8 frames. at one pipe in 1-2, all four kept dying in the same spot.
{:.aside}

The nudges are there because four copies alone didn't help much. It's the same model looking at the same situation, so the copies tend to make the same mistake. Now one does a running jump, one holds the jump longer, one waits a moment before jumping, and one backs up first. Each nudge lasts about a second before Jev takes over again. If all four still die, it splits again with nudges it hasn't tried, and after that it falls back to an older copy.

I started out calling the copies "trials" and later renamed them to "verses", because by then I was going for a multiverse theme. The verse that survives becomes canon, and the others collapse.

{% include figure.html src="/assets/posts/mario-never-dies/live-second-fork-4x3-v4.jpg" alt="A live run at its second fork, with four labeled verses, a compact timeline showing both forks, and the decision panel open." caption="a live run at its second fork. verses 5 to 8 are trying different recoveries, with the first fork still visible on the timeline." %}

there's a pipe in 1-2 where jev would back up a few pixels and walk into the same blocked jump, over and over.
{:.aside}

World 1-1 usually takes two or three deaths, but 1-2 is a lot harder. One of my runs died 54 times in there. The furthest I've seen it get is 1-3, where it ran out of retries, so the name oversells it a little.

## the numbers

one of mario's jumps takes about half a second. freezing the whole machine takes less.
{:.aside}

On my machine, freezing a copy of the running VM usually takes between 120 and 220ms. Turning one frozen copy into four running VMs takes about a quarter of a second, which I think is great! When you're watching, you don't even see it happen.

The only wait you notice is Jev's round trip, which was about a second per decision for me. That's understandable given I'm running this from my man cave in Lagos. In a live run, it means Mario takes a few steps, waits for the next answer, and takes a few more. Recordings don't have the problem, because they play back on game time and skip the waiting. A run that took five minutes live plays back in under a minute.

## the ui

I made the first UI with Codex, and it was terrible. What I got was basically a monitoring dashboard. It was noisy, and you couldn't tell where a snapshot or a branch happened, which is what the demo is supposed to show.

{% include figure.html src="/assets/posts/mario-never-dies/original-codex-ui-4x3-v3.jpg" alt="The first UI, a dark dashboard with a big headline, stats and probability bars around an empty game area." caption="the first ui. seven probability bars, five counters and a panel explaining the loop." %}

I switched to Claude's Fable model and redid the entire thing. I wanted something much simpler that didn't look like AI slop. What came back is what you have been looking at further up this post, and it is about ten times better.

The timeline under the game is what changed everything. Every frozen copy and every verse that died sits right there on it, which is the one thing the old dashboard ui didn't convey well.

## watching it back

Once there are four Marios on the screen, you want to pause and look at them, and then you want to go back and see what killed him. So I added playback controls.

There's also a toggle for watching just the canon timeline. It skips every stretch that ended in a death and cuts straight to the verse that survived. What's left is one run where Mario never dies.

## what's next

Next up is Flappy Bird. It's on the game menu, marked as "soon". I think it fits the idea even better than Mario does, because it's permadeath. There are no lives and no checkpoints, and one touch sends you back to the start. It works, but it's not where I want it to be yet.

The code is [open source](https://github.com/superradcompany/mario-never-dies). At some point it would be nice to run a fast model locally instead, so the whole thing is self-contained and there's no round trip to wait on. At the end of each run there's a "save the map" button that draws every timeline it took. If you try it, send me yours.
