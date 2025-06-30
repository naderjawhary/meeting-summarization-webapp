import whisperx
import gc
import time
import traceback

device = "cuda"
audio_file = r"E:\Master Thesis\WhisperX\LDC97S62.wav"
batch_size = 8  # reduce if low on GPU mem
compute_type = "int8"  # change to "float16" or "int8" based on GPU

print("🚀 Loading WhisperX model...", flush=True)
model = whisperx.load_model("large-v2", device, compute_type=compute_type)

print("📥 Loading audio...", flush=True)
audio = whisperx.load_audio(audio_file)
print("✅ Audio loaded.", flush=True)

try:
    print("📝 Starting transcription...", flush=True)
    start = time.time()
    result = model.transcribe(audio, batch_size=batch_size)
    end = time.time()
    print(f"\n✅ Transcription time = {end - start:.2f} seconds", flush=True)
    print("🔹 Segments before alignment:", flush=True)
    print(result["segments"], flush=True)
except Exception as e:
    print("❌ An error occurred during transcription.", flush=True)
    traceback.print_exc()

try:
    print("\n🔧 Starting alignment...", flush=True)
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    print("✅ Alignment complete.", flush=True)
    print("🔹 Segments after alignment:", flush=True)
    print(result["segments"], flush=True)
except Exception as e:
    print("❌ An error occurred during alignment.", flush=True)
    traceback.print_exc()
