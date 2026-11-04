---
layout: post
title: "Adding a Mic Button to a Web App: Five Ways to Build Voice Input, and Why a Server Relay Wins"
date: 2026-11-04
tags: [voice, speech-to-text, websocket, architecture, web]
description: "A practical comparison of browser speech recognition, record-and-upload, direct provider streaming, a backend WebSocket relay, and a WebRTC agent for dictation in web apps, with the reasons a relay is the default."
image: /assets/images/2026-11-04-web-app-voice-input-options-cover.jpg
---

![A microphone emitting teal sound waves through an amber relay node that resolve into lines of text](/assets/images/2026-11-04-web-app-voice-input-options-cover.jpg)

A mic button next to a chat box looks like a small feature. The user taps it, speaks, sees the words appear in the input, edits them if needed, and presses send. Nothing is spoken back. This is **dictation**: speech-to-text (STT) feeding an ordinary text field.

It is much simpler than a realtime voice conversation, where the assistant answers aloud, either side can interrupt, and turn-taking has to feel natural. Dictation needs none of that. It still raises one architectural question that is easy to get wrong: **where does the audio go, and who controls the connection to the recognizer?**

"Pick an online STT provider" answers only half of that. The provider decides recognition quality. The architecture decides latency, browser coverage, billing, abuse protection, and how painful it is to switch providers next year.

This article compares five ways to build it and explains why a backend WebSocket relay is the default I would pick for a product.

**Scope.** This is an architecture comparison, not a benchmark. Browser and vendor capabilities were checked against official documentation on **November 4, 2026**; latency notes are qualitative unless stated otherwise.

## 1. What actually decides the choice

Before comparing options, fix the requirements. For a dictation box in a product, these are the ones that separate the options:

| Requirement | Why it matters for dictation |
|---|---|
| **Live partial results** | Words should appear while the user is still talking. Waiting until they stop feels broken. |
| **Recognition quality** | Mixed languages, product names, and domain vocabulary are where recognizers differ most. |
| **Browser coverage** | A mic button that silently does nothing in one browser is a support ticket. |
| **Cost and metering** | Commercial STT is billed by audio time. If you pay per second, you probably want to meter per second. |
| **Provider portability** | STT quality moves fast. You will likely want to switch providers or models at least once. |
| **Credential safety** | A provider API key can never ship to the browser. |
| **Privacy** | Audio leaves the device in every cloud option; the question is to whom, and under which terms. |

## 2. Option A: the browser's built-in Web Speech API

The browser exposes `SpeechRecognition` (prefixed `webkitSpeechRecognition` in some engines). You start it, receive interim and final results, and write them into the text field. No API key, no backend, no bill.

```javascript
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!Recognition) hideMicButton();          // unsupported browser

const rec = new Recognition();
rec.lang = "en-US";
rec.interimResults = true;
rec.continuous = true;
rec.onresult = (e) => {
  let interim = "", final = "";
  for (const r of e.results) (r.isFinal ? (final += r[0].transcript) : (interim += r[0].transcript));
  renderDraft(final, interim);              // commit final text, show interim in grey
};
rec.start();
```

**What you get.** Streaming results with almost no code, at zero marginal cost to you. For everyday speech in a major language, quality in Chrome and Safari is usually good enough for a text box the user can edit.

**What you give up.**

- **Coverage.** Chrome and Edge support it (unprefixed since version 139, prefixed long before that). Safari supports the prefixed `webkitSpeechRecognition` since 14.1 on macOS and 14.5 on iOS. Release Firefox has not supported it; MDN's compatibility data lists support arriving in Firefox 160, scheduled for November 10, 2026. Feature-detect and hide the button where it is missing.
- **Control.** You cannot choose the model, and the same sentence is recognized by a different engine in each browser. Vocabulary control is limited: `SpeechGrammarList` is deprecated and has no effect on recognition services. Chrome 142 added `SpeechRecognition.phrases` for contextual biasing, but Safari has no equivalent.
- **Where the audio goes.** According to MDN, Chrome's recognition is server-based: audio is sent to a web service, so it does not work offline. Chrome 139 added an on-device path (`processLocally`, with `available()` and `install()`), but it is opt-in and needs a downloaded language pack. The recognition terms are the browser vendor's, not a contract you signed.
- **No SLA.** The recognizer is a browser feature, not a commercial API. Behavior can change with a browser release, and session limits are not under your control. In practice sessions also end on their own after a stretch of silence; MDN documents no limit, so handle `onend` and restart if you need long dictation.

**When to pick it.** Free dictation where "good enough in Chrome and Safari" is acceptable and you hide the button elsewhere. It is also a sensible stopgap while you build something better.

## 3. Option B: record, upload, transcribe

Capture audio with `MediaRecorder`, upload the file when the user stops, and let your backend call a batch transcription API.

This is the easiest server-side integration and it gives you full control: the key stays on the server, you meter exact durations, and switching providers is a backend deploy.

For dictation it has one disqualifying property: **nothing appears until the user stops talking**, and then they wait for upload plus transcription. A ten-second utterance can take several more seconds to show up. Users read that silence as "it didn't hear me" and start over.

Batch transcription is the right tool for voice memos, uploaded recordings, and meeting notes. It is the wrong tool for a text box where the user is watching the cursor.

That leaves streaming. There are three ways to stream audio to a recognizer from a web page.

## 4. Option C1: the browser streams directly to the provider

Your backend mints a **short-lived, single-use token**; the browser opens the provider's realtime WebSocket (or WebRTC session) with it and streams audio directly. Several STT vendors document exactly this pattern for client-side apps. For example, ElevenLabs issues single-use [`realtime_scribe` tokens](https://elevenlabs.io/docs/api-reference/tokens/create) that expire after 15 minutes; OpenAI's Realtime API issues [ephemeral client secrets](https://developers.openai.com/api/reference/resources/realtime/subresources/client_secrets/methods/create) (10 minutes by default) that also cover transcription-only sessions; Deepgram's [grant endpoint](https://developers.deepgram.com/reference/auth/tokens/grant) issues JWTs with a 30-second default TTL.

```text
Browser ──(1) POST /stt-token──► Your backend ──► Provider: mint short-lived token
Browser ──(2) WebSocket + token ─────────────────► Provider realtime STT
Browser ◄─(3) partial / final transcripts ───────── Provider
```

**Strengths.** Lowest latency (one network hop), no long-lived connections on your servers, and the smallest amount of backend code: one token endpoint.

**Weaknesses.** Once the token is issued, the session belongs to the client.

1. **Provider lock-in moves into your client.** The provider's URL, message format, and parameters live in front-end code. Switching providers means a front-end release. For a web app that is a deploy; for the mobile builds of the same product it is a store release and a long tail of old clients still talking to the old provider.
2. **Metering is approximate.** Your server knows a token was issued, not how many seconds were streamed. To charge per second you must trust the client's report or reconcile against the vendor's usage data afterward.
3. **Abuse surface.** A token can be extracted and used outside your app. Single-use and short expiry limit the damage, but the mint endpoint needs authentication and rate limiting.
4. **Domain logic is duplicated.** Vocabulary hints, language settings, and fallback rules end up written in the client, separately from any server-side voice features you already have.
5. **No server-side observability or fallback.** If the provider degrades, the server never sees it and cannot fail over.
6. **Content Security Policy.** The provider's WebSocket origin must be allowed in `connect-src`.

**When to pick it.** Dictation is free (or billed per use, not per second), you do not expect to change providers soon, and latency matters more than control.

## 5. Option C2: a backend WebSocket relay

The browser streams audio to **your** WebSocket endpoint. Your server authenticates the user, opens the upstream connection to the provider with the key it holds, forwards audio up and transcripts down, and meters the session.

```text
Browser ──PCM frames──► Your relay ──PCM frames──► Provider realtime STT
Browser ◄──transcripts── Your relay ◄──transcripts── Provider
                          │
                          └─ auth · vocabulary · metering · caps · logs · fallback
```

**Strengths.**

- **Provider choice is a server setting.** Switching vendors, models, or parameters is a backend deploy. Every client, including old mobile builds, moves at once.
- **Exact, server-authoritative metering.** The relay sees every audio frame. Seconds of audio are `bytes / (sample_rate × bytes_per_sample)`, measured on your side, so per-second billing does not depend on the client.
- **Enforced limits.** Maximum session length, concurrent sessions per user, and balance checks happen in one place, before the provider is billed.
- **Shared domain logic.** Vocabulary hints and language defaults live next to the rest of your backend instead of being re-implemented in each client.
- **Observability and fallback.** Error rates and time-to-first-word are visible in server logs, and the relay can retry or switch to a secondary provider.

**Weaknesses.**

- **One extra hop.** Typically tens of milliseconds within the same region, which users do not perceive in a stream of partial words. Put the relay near the provider's region.
- **Long-lived connections on your servers.** Each dictation session holds a WebSocket open for its duration. On a request-based platform, that connection occupies capacity for the whole time. On Google Cloud Run, for example, [WebSockets are treated as long-running HTTP requests](https://cloud.google.com/run/docs/triggering/websockets): they are subject to the instance's concurrency limit and are closed at the [request timeout](https://cloud.google.com/run/docs/configuring/request-timeout) (5 minutes by default, 60 at most), so clients must handle reconnects. Dictation sessions are short (seconds to a minute or two), which keeps this manageable; set a hard cap anyway.
- **More code than C1.** You own the relay, its backpressure, and its error mapping.

## 6. Option C3: a WebRTC room with a server-side agent

Use a realtime media platform (LiveKit, or a similar SFU) the way realtime voice assistants do. The browser publishes its microphone track to a room; a server-side agent subscribes, runs STT, and sends transcripts back over a data channel.

**Strengths.** WebRTC runs over UDP with congestion control and loss recovery designed for live audio, so it degrades more gracefully on lossy mobile networks than a TCP WebSocket. If you already run a voice agent, its STT configuration, fallback chain, and usage accounting can be reused.

**Weaknesses.** It is the heaviest option for the smallest feature: a room, an agent dispatch, and a worker per session, plus the platform's per-minute charges on top of STT. Joining a room and dispatching an agent adds start-up delay before the first word.

It is a common misconception that this option produces **better recognition**. It does not. All three streaming options can use the same STT model, and the model determines accuracy. What C3 adds is a more resilient transport and reuse of an existing voice pipeline. Server-side control, the property most people actually want, is equally available in C2.

**When to pick it.** Users dictate long passages on poor mobile networks or in noisy places, or you already operate a WebRTC voice agent and want one pipeline for both features.

## 7. Side-by-side

| | A. Web Speech API | B. Record + upload | C1. Direct to provider | C2. Backend relay | C3. WebRTC + agent |
|---|---|---|---|---|---|
| Partial results while speaking | Yes | **No** | Yes | Yes | Yes |
| Recognition quality | Browser vendor's | Your choice | Your choice | Your choice | Your choice |
| Consistent across browsers | No | Yes | Yes | Yes | Yes |
| Backend code | None | Upload endpoint | Token endpoint | WebSocket relay | Room + agent worker |
| Switch provider without client release | n/a | Yes | **No** | Yes | Yes |
| Server-authoritative metering | n/a | Yes | **No** | Yes | Yes |
| Server-side vocabulary and fallback | No | Yes | No | Yes | Yes |
| Extra latency | None | Seconds | Lowest | One hop | Room join + agent |
| Packet-loss resilience | Browser-managed | n/a | TCP | TCP | **UDP / WebRTC** |
| Marginal cost | **Free to you** | STT | STT | STT + relay capacity | STT + media platform + worker |

## 8. Why the relay is my default

For a product, three things tend to be true at once:

1. **The recognizer will change.** Especially outside English, the best realtime STT model a year from now is unlikely to be the one you start with. C2 makes that a server change.
2. **Dictation costs money per second, so it eventually gets metered.** Even if it is free today, a relay lets you add limits or pricing later without trusting the client.
3. **Server-side control is what matters, not the transport.** Vocabulary hints, caps, logging, and fallback are the features that improve over time, and they all live on the server in C2.

C1 is a good choice only when the first two are false. C3 is a good choice only when transport resilience is a real requirement or a WebRTC agent already exists. Option A remains a useful free tier or stopgap, with the button hidden where it is unsupported.

## 9. Building the relay: a minimal shape

The sketch below shows the moving parts; the provider client is an interface you implement against your vendor's realtime API.

**Client: capture 16 kHz mono PCM and stream it.**

```javascript
// pcm-worklet.js — runs on the audio thread
class PcmWorklet extends AudioWorkletProcessor {
  process([input]) {
    const ch = input[0];
    if (ch) {
      const pcm = new Int16Array(ch.length);
      for (let i = 0; i < ch.length; i++) pcm[i] = Math.max(-1, Math.min(1, ch[i])) * 0x7fff;
      this.port.postMessage(pcm.buffer, [pcm.buffer]);
    }
    return true;
  }
}
registerProcessor("pcm-worklet", PcmWorklet);
```

```javascript
const stream = await navigator.mediaDevices.getUserMedia({
  audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 },
});
const ctx = new AudioContext({ sampleRate: 16000 });   // resample in the worklet if unsupported
await ctx.audioWorklet.addModule("/pcm-worklet.js");
const node = new AudioWorkletNode(ctx, "pcm-worklet");
ctx.createMediaStreamSource(stream).connect(node);

const ws = new WebSocket("wss://api.example.com/ws/dictation");
ws.binaryType = "arraybuffer";
ws.onopen = async () => ws.send(JSON.stringify({ type: "start", token: await getIdToken(), lang: "auto" }));
node.port.onmessage = (e) => ws.readyState === 1 && ws.send(e.data);
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === "partial") showInterim(msg.text);
  if (msg.type === "final") commitText(msg.text);
};
```

Browsers cannot set an `Authorization` header on a WebSocket, so the token travels in the first message. A subprotocol or a short-lived ticket in the query string also works; avoid long-lived credentials in URLs, which end up in logs.

**Server: authenticate, meter, forward (FastAPI sketch).**

```python
SAMPLE_RATE, BYTES_PER_SAMPLE = 16_000, 2
MAX_SECONDS = 120

@app.websocket("/ws/dictation")
async def dictation(ws: WebSocket):
    await ws.accept()
    start = await asyncio.wait_for(ws.receive_json(), timeout=5)
    user = await verify_id_token(start["token"])          # never trust a client-sent user id
    session = await meter.open(user, max_seconds=MAX_SECONDS)

    async with stt.connect(language=start.get("lang"), vocabulary=vocab_for(user)) as upstream:
        async def audio_up():
            async for frame in ws.iter_bytes():
                session.add_seconds(len(frame) / (SAMPLE_RATE * BYTES_PER_SAMPLE))
                if session.over_limit():
                    break
                await upstream.send_audio(frame)
            await upstream.finish()

        async def text_down():
            async for event in upstream.events():         # partial / final
                await ws.send_json({"type": event.kind, "text": event.text})

        try:
            await asyncio.gather(audio_up(), text_down())
        finally:
            await session.close()                          # write usage once, server-side
```

## 10. Details that bite in production

- **Insert at the cursor, not at the end.** Users dictate into the middle of a draft. Track the selection when recording starts and replace the interim span, not the whole field.
- **Interim text is not committed text.** Render it differently and replace it on every update; only `final` segments are appended.
- **Cap the session on the server.** A forgotten tab with an open microphone is billed audio. Combine a hard maximum with a silence timeout.
- **Pick one audio format and resample once.** Most realtime STT APIs want 16-bit PCM at a fixed sample rate. `MediaRecorder` gives you Opus in WebM or MP4 containers, which many realtime endpoints do not accept.
- **Permissions and secure contexts.** `getUserMedia` requires HTTPS (or `localhost`), and mobile Safari only starts audio capture after a user gesture.
- **Close cleanly.** Send an explicit end-of-audio message upstream so the provider flushes the last words; otherwise the final few hundred milliseconds are often lost.
- **Disclose where audio goes.** Every cloud option sends voice to a third party. Say so in the privacy policy, including for the browser's built-in recognizer.

## Summary

- **Dictation is STT into a text box**, not a voice conversation. Keep it that simple.
- **Batch upload is wrong for a live text box**: no words appear until the user stops.
- **The browser's Web Speech API is free and streaming**, but gives you no control and incomplete browser coverage.
- **Among streaming options, the model decides accuracy; the architecture decides control.** A direct connection is fastest and simplest; a WebRTC agent is the most resilient transport; a **backend WebSocket relay** gives server-authoritative metering, provider portability, and shared domain logic at the cost of one hop and some connection capacity.
- For most products, start with the relay.
