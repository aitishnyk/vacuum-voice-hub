# Adding a voice pack

Add a record to `catalog/voices.json` with:
- stable `id`;
- title/language/tags/adult flag;
- upstream author/project/source page;
- raw artifact URL when legally appropriate;
- source format adapter;
- pinned size + integrity hash;
- attribution text;
- redistribution status.

If the archive uses a new event layout, add a source-format adapter instead of hardcoding the pack into a model adapter.
