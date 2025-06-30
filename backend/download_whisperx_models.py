import whisperx

device = "cuda"  # or "cpu" if you don't have a GPU
compute_type = "int8"  # use "float16" or "float32" for more precision (if supported)

models_to_download = [
    "small",
    "medium"
]

for model_name in models_to_download:
    print(f"\n🔽 Downloading and loading model: {model_name}")
    try:
        model = whisperx.load_model(model_name, device=device, compute_type=compute_type)
        print(f"✅ Model {model_name} loaded and cached successfully.")
    except Exception as e:
        print(f"❌ Failed to load model {model_name}: {e}")
