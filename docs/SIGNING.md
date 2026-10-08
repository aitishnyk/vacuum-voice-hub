# Signing and Notarization Boundary

Vacuum Voice Hub does not claim cryptographic signing merely because an artifact was built successfully.

## Release manifest

`release-manifest.json` contains:

```json
{
  "signature": {
    "scheme": "ed25519",
    "status": "unsigned",
    "key_id": null,
    "detached_signature": null
  }
}
```

This is the only valid state for ordinary CI/source builds.

## Future trusted signing gate

A production signing environment may:
1. verify `SHA256SUMS`;
2. verify the unsigned release manifest;
3. collect exact desktop artifacts from the successful macOS/Windows/Linux build;
4. record their SHA-256 hashes;
5. sign the final canonical manifest with an offline/protected Ed25519 key;
6. publish the detached signature and public key ID.

The private signing key must never be stored in the repository or emitted to build logs.

## macOS

A distributable macOS app may later require:
- Developer ID Application signing;
- hardened runtime;
- notarization;
- stapling.

Current CI **does not claim** any of these.

## Windows

A distributable Windows binary may later require Authenticode signing with a protected code-signing certificate.

Current CI **does not claim** Authenticode signing.

## Linux

Linux artifacts currently rely on SHA-256/release-manifest integrity. Distribution-specific package signing can be added when package formats are introduced.

## Claim rule

Use the following vocabulary:
- **built** — PyInstaller/build workflow succeeded;
- **checksum verified** — release hash verification succeeded;
- **signed** — only when a verifiable cryptographic signature exists;
- **notarized** — only when the platform notarization service has accepted the exact artifact.
