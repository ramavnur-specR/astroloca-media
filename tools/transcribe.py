import json, re, subprocess, sys
import soundfile as sf, sherpa_onnx
src, out = sys.argv[1], sys.argv[2]
M = "/home/claude/work/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8"
wav = src.replace(".mp4", ".wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", wav], check=True)
audio, sr = sf.read(wav, dtype="float32")
dur = len(audio) / sr
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "silencedetect=noise=-35dB:d=0.3", "-f", "null", "-"], capture_output=True, text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
mids = [(a + b) / 2 for a, b in zip(ss, se)]
cuts, last = [0.0], 0.0
for m in mids:
    if m - last >= 18:
        cuts.append(m); last = m
cuts.append(dur)
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx", joiner=f"{M}/joiner.int8.onnx",
    tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=4)
toks = []
for a, b in zip(cuts, cuts[1:]):
    s = rec.create_stream()
    s.accept_waveform(sr, audio[int(a * sr):int(b * sr)])
    rec.decode_stream(s)
    r = s.result
    for t, ts in zip(r.tokens, r.timestamps):
        toks.append([t, round(a + ts, 3)])
json.dump(toks, open(out, "w"))
print("".join(t for t, _ in toks).strip())
