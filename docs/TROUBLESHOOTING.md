# Troubleshooting

| Symptom | Recovery |
| --- | --- |
| App does not open | Verify checksum and architecture. Read the signing status. Source users can run `vvh web --port 8787` and open the printed loopback URL to isolate GUI-library issues. |
| Missing decoder | Reinstall `imageio-ffmpeg`; desktop builders must collect its executable. Try a PCM WAV. |
| No sound | Press Play explicitly, check OS output/volume and player duration. Test another event; optional TTS is not needed for bundled samples. |
| File rejected | Use WAV/MP3/OGG/FLAC/M4A/AAC/Opus, below the 25 MiB clip limit. Corrupt files must be re-exported from the original recording. |
| Demo integrity error | Reinstall a verified package; do not bypass its asset hashes. Start a new demo session after repairing the installation. |
| Package cannot build | Choose the exact model, run Coverage/Preflight and assign at least five mapped target events. Build success does not prove complete coverage. |
| Model cannot install | Read transport policy. Offline creation remains useful; there is no supported override that creates hardware evidence. |
| Export fails | Check free disk space and write permission. Retry with a new output; preserve original recordings. Demo export names are unique. |
| Backup restore fails | Run `vvh creator backup-verify backup.zip`; restore into a new empty destination. Never patch over a damaged live project. |
| Optional Piper/eSpeak missing | Install the engine locally and obtain a properly licensed model, or use recordings instead. |

Use [Issues](https://github.com/aitishnyk/vacuum-voice-hub/issues) with version,
OS, architecture, signing status, safe reproduction steps and sanitized errors.
Do not attach private recordings, robot tokens, IP/MAC addresses or home paths.
