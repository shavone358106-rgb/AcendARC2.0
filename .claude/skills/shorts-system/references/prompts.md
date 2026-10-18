# The 11 starter prompts (from the Shortify guide)

Fill in every [BRACKET]. The `make` command automates 1, 2, 6, 7, 8, 9 and 11; use the rest by hand or let the skill run them.

## Prompt 1: Steal a proven hook (Write)

```
Here is a proven hook, word for word: "[WINNING HOOK]"
Source: [LINK], [VIEWS] views. The creator's median is [MEDIAN VIEWS].
My topic: [TOPIC]. My real numbers: [NUMBERS + WHERE EACH ONE IS FROM].
First check the ratio. If views are under 3x the median, stop and tell me to
pick a different hook. Adapt it to my topic. Keep every other word and the word
order. Swap only the slots: the tool, the topic, the number, the audience.
Give me 3 versions. For each, show the share of original words you kept (aim
for 70% or more) and what you swapped.
Then read each one as a stranger who has never heard of me. Flag any word that
won't make sense cold: inside terms, jargon, "it" or "this" with nothing to
point at. Never add a number I didn't give you.
```

## Prompt 2: Lock the script with a cold read (Check, subagent)

```
Here's my short script: [SCRIPT]. The lane is [TOP / MIDDLE / BOTTOM] and the
last line must be: "[CTA LINE]".
Use a subagent that has never seen this project to check it before I record
anything:
1) Read every line as a stranger. Flag any line that isn't clear on its own,
and offer a plainer one.
2) Line 2 names the viewer's real problem in plain words.
3) Steps say "First" and "Then" out loud.
4) Every line ends on a noun or number a graphic can show.
5) 105 to 125 words. No hype word without a number next to it.
6) Money is written as words for the voice ("five dollars and seventy cents").
Numerals only in captions and graphics.
7) Every number has a source I gave you. Cut any that don't.
Return the fixed script and a list of what changed and why. Once I say
"locked", don't change a word.
```

## Prompt 3: Lock my look (Style sheet)

```
Help me write a one-page style sheet for my short videos. My vibe is [3 WORDS,
e.g. dark, bold, techy]. Here are 2 or 3 creators or screenshots I like: [LINKS
OR IMAGES]. Give me: a dark look and a light look, one accent color for each,
one or two fonts, how captions look, how things move in and out, and 5 things I
should never do. Rule for every choice: a stranger reads any frame in about one
second. Keep it simple, bold, big and clean. Save it as [FOLDER]/STYLE.md.
```

## Prompt 4: Study creators frame by frame (Research, subagents)

```
I want to learn how these creators build their short videos: [LINK 1], [LINK
2], [LINK 3]. Start one subagent per video, all at the same time. Each one
should: download the video, pull a frame every 0.5 seconds, get the transcript
with timestamps, and write down: how long the hook holds, how often something
new appears on screen, when the face shows, what the captions look like, what
graphic sits under each type of line, and how the cover and the post caption
work.
Each subagent saves notes to [FOLDER]/creator-name.md and reports back in under
150 words. Then combine them into one list of rules I could copy, with the
timestamp that proves each rule.
```

## Prompt 5: Build a graphics library and its guide (Build, subagents)

```
Using [FOLDER]/STYLE.md, build a small library of reusable motion graphics for
9:16 video in [HyperFrames / Remotion / After Effects]. Start with 6: a big
number that counts up, a list that adds one row per spoken word, a step ladder,
a before/after, a prompt typing into the Claude app and getting an answer, and
my ending card with a comment keyword. One subagent per graphic. Each takes
text and timing as inputs, renders a 3-second test and saves a still.
Then write a one-page guide: which graphic for which kind of line (claim,
number, list, steps, prompt, opinion, hook, ending), when to cut and when to
keep building, a "never do" list, and the lines we have no graphic for yet.
Save it as [FOLDER]/GRAPHICS.md.
```

## Prompt 6: QA this render frame by frame (Check, subagent)

```
Use a subagent to QA [VIDEO FILE]. Pull 3 frames per second and put them on
contact sheets, then open the frames at full size. List each problem with its
timestamp: text cut off or too small on a phone, empty or black frames, a
screenshot you can't read in a second, captions on top of a graphic, something
shown before it's said, beats too short to read, a cut during the hook, text in
the app's safe zones. Also check length ([TARGET] seconds) and loudness.
Return the list, worst first. Then fix them, render again, and repeat until the
list is empty. Save the sheets so I can look too.
```

## Prompt 7: Dissect a script into visual moments (Plan, subagent)

```
Take the locked script at [SCRIPT FILE] and the word timestamps from [AUDIO OR
AVATAR FILE]. Use a subagent to split every sentence into small visual moments.
For each: start and end time, its job (hook, claim, number, list item,
payoff...), the nouns you can draw, and the verb. The verb picks the motion
(turns into = morph, pick = pick, one to all = zoom out, send to = show it
being sent). Then pick what to show from [FOLDER]/GRAPHICS.md: the real thing,
a graphic, or my face. Rules: the hook has no cuts; anything under half a
second is a step on the current graphic; claims show proof within 2 seconds;
every screenshot must read in one second at phone size, or we build our own
graphic instead. Show me the plan as a table before building.
```

## Prompt 8: Check a trigger word (Check)

```
I want [WORD] as the comment keyword for a short about [TOPIC]. Check it's free
before I write the script. Look in my keyword list at [FILE], every comment-to-
DM automation in [MY DM TOOLS], and my last [NUMBER] post captions. Reject it
if it's used anywhere, if it's a common word people type anyway (yes, love,
info, link), or if it's hard to spell after hearing it once. If it fails,
suggest 5 short, fun, sayable words tied to the topic and check those too.
When one passes, add it to my list as reserved, with the topic and today's
date. Never reuse a word that was retired.
```

## Prompt 9: Captions for every platform (Write)

```
Write post captions for my short. Script: [SCRIPT]. The comment gets: [THE
THING]. Keyword: [WORD]. Link: [LINK].
Instagram and Facebook: line 1 is exactly
Comment "[WORD]" to get [the thing] + [the result].
Then a blank line, then the hook and the script as short one-line paragraphs.
TikTok, YouTube, X and LinkedIn: no comment promise, since nothing answers
comments there. Same hook and body, then end with the link. Five hashtags at
most per platform. Plain words, no hype. Save one block per platform in one
file, ready to paste.
```

## Prompt 10: Cover prompt skeleton (Image)

```
A 9:16 short-video cover. Image 1 is my face. Image 2 is the [TOOL] logo. Top:
that logo and the name "[TOOL NAME]" in large clean type. Middle: my face,
centered, smiling, wearing [WHAT I WEAR], lit with bright, even studio light
and true skin tones. Two equal app tiles at ear level, one each side, slightly
behind my head: [TOOL 1] and [TOOL 2]. Under my chin, a tight two-line title: "
[LINE 1]" / "[LINE 2]", line 2 on a [ACCENT COLOR] bar. Leave the top and
bottom 13% empty.
```

## Prompt 11: Turn it all into a skill (Skill)

```
We've now made shorts by hand [NUMBER] times. Turn this into a Claude Code
skill called [NAME] that takes one topic and makes one short.
Steps: 1) read the topic card and its lane, 2) reserve a keyword that passes
the check, 3) adapt a proven hook, 4) write the script and run the cold read,
then stop until I say "locked", 5) voice and face, 6) dissect, 7) build, 8) QA
until the list is empty (subagent), 9) captions per platform and a cover, 10)
stop and show me everything.
Point to STYLE.md and GRAPHICS.md instead of copying them in. Log what each
short spent. It must never post or schedule anything until I say go in that
chat. Keep a list of the mistakes we fixed so it doesn't repeat them.
```
