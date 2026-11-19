# Docker Facebook Demucs
This repository dockerizes [Demucs](https://github.com/adefossez/demucs)
to split music tracks into different tracks (bass, drums, voice, others).

## Usage
### Clone this repository
```bash
git clone https://github.com/xserrat/docker-facebook-demucs.git demucs
```

### Split a music track on the AMD Radeon RX 9060 XT

Use the Windows ROCm environment installed in `models\windows-rocm`. Put your track in `input`, then run this in PowerShell. Change `$track` for each song.

```powershell
Set-Location -LiteralPath 'T:\Documents\__code\demucs'
$track = 'thankGodImFree.mp3'
$env:Path = "$(Join-Path $PWD 'models\windows-rocm\tools\ffmpeg-8.1.2-full_build-shared\bin');$env:Path"
$env:TORCH_HOME = Join-Path $PWD 'models'
& .\models\windows-rocm\venv\Scripts\python.exe .\demucs-rocm.py -n htdemucs -d cuda:0 --out .\output ".\input\$track"
```

The WAV stems go to `output\htdemucs\thankGodImFree\`. For example, set `$track = 'moreThanAble.mp3'` to write stems to `output\htdemucs\moreThanAble\`. ROCm PyTorch uses `cuda:0` for the first AMD GPU. The launcher uses SoundFile for WAV and FLAC output on Windows.

#### Higher-quality separation with `htdemucs_ft`

Use the fine-tuned model when separation quality matters more than speed. The command selects your Radeon GPU with `-d cuda:0`. The fine-tuned model can produce slightly better stems and takes about four times as long. [Demucs model guide](https://github.com/facebookresearch/demucs#separating-tracks)

```powershell
Set-Location -LiteralPath 'T:\Documents\__code\demucs'
$track = 'thankGodImFree.mp3'
$env:Path = "$(Join-Path $PWD 'models\windows-rocm\tools\ffmpeg-8.1.2-full_build-shared\bin');$env:Path"
$env:TORCH_HOME = Join-Path $PWD 'models'
& .\models\windows-rocm\venv\Scripts\python.exe .\demucs-rocm.py -n htdemucs_ft -d cuda:0 --out .\output ".\input\$track"
```

The first run downloads the fine-tuned model weights. This example writes four WAV stems to `output\htdemucs_ft\thankGodImFree\`, so you can compare them with the default model's stems in `output\htdemucs\thankGodImFree\`.

### Run with Docker in Windows PowerShell

Put your audio file in the repository's `input` folder. Start Docker Desktop and wait for its Linux engine to be ready. Build the image once from the repository folder. Use the `demucs-local:latest` tag so these examples use the image built from this repository's Dockerfile.

```powershell
Set-Location -LiteralPath 'T:\Documents\__code\demucs'
docker --context desktop-linux build -t demucs-local:latest .
```

Wait for the build to finish successfully before running the commands below. Run this command each time you want to split a track with `htdemucs`. Change `$track` to the filename in `input`.

```powershell
Set-Location -LiteralPath 'T:\Documents\__code\demucs'
$track = 'thankGodImFree.mp3'
docker --context desktop-linux run --rm --pull=never `
  -v "${PWD}\input:/data/input" `
  -v "${PWD}\output:/data/output" `
  -v "${PWD}\models:/data/models" `
  --entrypoint python3 demucs-local:latest `
  -m demucs -n htdemucs --out /data/output "/data/input/$track"
```

This example writes four WAV stems to `output\htdemucs\thankGodImFree\`.

To extract vocals and an accompaniment as MP3s, add `--two-stems vocals --mp3`.

```powershell
Set-Location -LiteralPath 'T:\Documents\__code\demucs'
$track = 'moreThanAble.mp3'
docker --context desktop-linux run --rm --pull=never `
  -v "${PWD}\input:/data/input" `
  -v "${PWD}\output:/data/output" `
  -v "${PWD}\models:/data/models" `
  --entrypoint python3 demucs-local:latest `
  -m demucs -n htdemucs --out /data/output --two-stems vocals --mp3 "/data/input/$track"
```

This example writes `vocals.mp3` and `no_vocals.mp3` to `output\htdemucs\moreThanAble\`.

If a command using `xserrat/facebook-demucs:latest` reports `unrecognized arguments: -j`, build `demucs-local:latest` as shown above and use the PowerShell examples in this section.

### Split a music track with Make
1. Copy the track you want to split into the `input` folder (e.g., `input/mysong.mp3`).
2. Execute `demucs` via the `run` job in the `Makefile`, specifying the `track` argument with only the name of the file:
```bash
make run track=mysong.mp3
```

This process will take some time the first time it is run, as the execution will:
* Download the Docker image that is setup to run the `facebook demucs` script.
* Download the pretrained models.
* Execute `demucs` to split the track.

Subsequent runs will not need to download the Docker image or download the models, unless the model specified has not yet been used.

#### Options
The following options are available when splitting music tracks with the `run` job:

Option | Default Value | Description
--- | --- | ---
`gpu`           | `false` | Enable Nvidia CUDA support (requires an Nvidia GPU).
`model`         | `demucs`| The model used for audio separation. See https://github.com/facebookresearch/demucs#separating-tracks for a list of available models to use.
`mp3output`     | `false` | Output separated audio in `mp3` format instead of the default `wav` format.
`shifts`        | `1`     | Perform multiple predictions with random shifts (a.k.a the shift trick) of the input and average them. This makes prediction `SHIFTS` times slower. Don't use it unless you have a GPU.
`overlap`       | `0.25`  | Control the amount of overlap between prediction windows. Default is 0.25 (i.e. 25%) which is probably fine. It can probably be reduced to 0.1 to improve separation speed.
`jobs`          | `1`     | Specify the number of parallel jobs to run during separation. This will multiply the amount of RAM used by the same number, so be careful!
`splittrack`    |         | Individual track to split/separate from the others (e.g., you only want to separate drums). Valid options are `bass`, `drums`, `vocals` and `other`. Other values may be allowed if the model can separate additional track types.

Example commands:
```bash
# Use the "fine tuned" demucs model
make run track=mysong.mp3 model=htdemucs_ft

# Enable Nvidia CUDA support and output separated audio in mp3 format
make run track=mysong.mp3 gpu=true mp3output=true
```

### Run Interactively

To experiment with other `demucs` options on the command line, you can also run the Docker image interactively via the `run-interactive` job. Note that only the `gpu` option is applicable for this job.

Example:
```bash
make run-interactive gpu=true
```

## Building the Image

The Docker image can be built locally via the `build` job:
```bash
make build
```

## License
This repository is released under the MIT license as found in the [LICENSE](LICENSE) file.
