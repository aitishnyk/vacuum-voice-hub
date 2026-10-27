# Owner launch actions

## Social preview

Open https://github.com/aitishnyk/vacuum-voice-hub/settings while signed in as
an administrator. Under Social preview, choose Edit → Upload an image and
select `vacuum_voice_hub/brand/social.png` (1200×630). Save and verify that
the repository's share preview uses it. API access alone does not provide
this UI upload; no private login credential should be copied into automation.

## Native acceptance and signing

Run the exact build and runtime commands in [Platform acceptance](PLATFORM_ACCEPTANCE.md).
Do the audible playback/relaunch check on each advertised platform. Keep native
reports with their exact artifact hashes. Do not promote untested architectures.
Apple Developer and Windows signing require real organization credentials;
otherwise publish only explicitly unsigned developer/beta assets after acceptance.

## Publish a prepared draft only after gates pass

```sh
gh release view v2.1.0 --repo aitishnyk/vacuum-voice-hub --json isDraft,assets,targetCommitish
```

PASS before publishing requires: exact reviewed target commit, actual assets
and SHA256SUMS, matching source/provenance, platform reports, completed native
playback/relaunch and matching local/draft checksums. A draft does not
create a verified public download. Inspect its report and finish missing native
gates before using `gh release edit v2.1.0 --draft=false --prerelease`.
This is an unsigned limited-platform beta until the stronger gates are met.
After publication run `scripts/verify_download.py` against every actual public
asset URL before advertising a tested download. Never edit v2.0.0 or silently replace a published binary.

## Hosted CI failures before steps

```sh
gh run list --repo aitishnyk/vacuum-voice-hub --limit 10
gh run view RUN_ID --repo aitishnyk/vacuum-voice-hub --json jobs,conclusion
```

The v2.1 PR annotations state: "The job was not started because your account
is locked due to a billing issue." The account owner must resolve the billing
lock in GitHub account settings, then rerun one source CI workflow. Jobs with
no executed steps are infrastructure failures, not passing software tests. Do not repeatedly dispatch expensive desktop workflows.
Local acceptance commands remain in Developer guide.

## Pages recovery

The canonical static build can be deployed from the existing `gh-pages` branch.
To inspect:

```sh
gh api repos/aitishnyk/vacuum-voice-hub/pages
gh api repos/aitishnyk/vacuum-voice-hub/pages/builds/latest
```

Expected success is a public URL returning HTTP 200 with the current catalog
manifest. If Pages needs enabling after the branch exists:

```sh
gh api --method POST repos/aitishnyk/vacuum-voice-hub/pages \
  -f 'source[branch]=gh-pages' -f 'source[path]=/'
```

Do not call a pending build published. `public-site.yml` regenerates from
canonical sources and appends a normal commit to the publishing branch.
