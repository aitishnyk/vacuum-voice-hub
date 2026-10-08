# Security & privacy

- Local tokens are secrets. VVH reads them interactively or from the current process and never prints them.
- The local web UI binds to `127.0.0.1` only.
- Archive extraction rejects absolute paths, `..`, symlinks and hard links.
- Remote artifacts are verified before extraction.
- Model identity is checked before installation.
- The temporary file server exposes only the generated package directory and is stopped after install.
- Xiaomi UID/DID is not required for the supported local X10 path.
