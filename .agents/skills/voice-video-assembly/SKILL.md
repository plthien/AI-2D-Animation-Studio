---
name: voice-video-assembly
description: Reuse YTB Kokoro/ElevenLabs voice, forced alignment, audio validation and FFmpeg host for P8–P9 with voice-last 24FPS timing reconciliation.
---

# Skill — voice-video-assembly

## References

`MASTER_SPEC.md` §11.2–11.5, §0.2, Appendix A P8/P9; YTB `kokoro/`, voice provider registry/adapters/alignment and FFmpeg process/diagnostic modules only.

## Procedure

1. Port exact YTB voice core while avoiding voice-first Scene Breakdown, BeatTimingMap and legacy beat assembly. Preserve Kokoro frozen runtime identity and 48kHz normalized audio; ElevenLabs forced alignment remains timing authority.
2. For each voice cue bind frozen narration span to shot/section; validate exact text and provider identity, normalized mono PCM16 48kHz, empty/overrun/mismatch cases.
3. Map aligned audio windows to 24 FPS (2000 PCM samples/frame) with exact integer time authority. Bounded holds/stretch only on author-approved flexible intervals. Never shift contact/impact or character actions silently.
4. Create final_timeline.v1 and selectively rerender only affected shots using frozen rig and action inputs; ffmpeg mux to H.264 yuv420p/AAC with correct duration.
5. Analyze clipping, silence, narration content, encode/ffprobe stream/frame counts and corruption; enforce QC fail states.
6. Tests include prepared synthetic audio only as transport smoke; record separately from actual Kokoro and forced alignment Windows/provider passes.

## Acceptance

One 48kHz authoritative timeline, no voice-first authoring dependency, no video/image fallback and no fake TTS completion.


## Mandatory animation-first v1.2 amendment

Only voiced shots receive WAV/VoiceCue. Silent visual shots remain duration-correct and receive exact 2000 zero samples/frame at final assembly, with no fabricated voice artifact. Voice remains last; no dialogue/lip-sync in MVP.

## Mandatory phase implementation authority

Read `docs/implementation/INDEX.md` and the matching full `Pxx_*.md` plan before writing code; run `tools/validate_implementation_pack.py` and `tools/test_cross_phase_contracts.py` as part of this skill. Phase plan adds executable work orders but cannot override Master Spec or normative JSON Schema.
