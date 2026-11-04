# Canvas AI Studio API contracts

These JSON Schema (2020-12) files describe **planned** AI Studio data and requests; they do not imply deployed endpoints or active model training.

- `reference.schema.json`: provenance, 64×64 normalization metadata, training/redistribution permission, body plan, tags, dedupe hash, family-based split.
- `training-request.schema.json`: real train/fine-tune job inputs, selected dataset snapshot, architecture and checkpoint.
- `generation-request.schema.json`: 64×64 candidate request, checkpoint selection, prompt/tags, optional base sprite and mask, palette, deterministic seed.

The backend must validate request schemas and additionally check authorization, rights, dataset completeness, model capabilities, file safety, and account quotas. A valid JSON request does **not** mean a compatible trained model exists.

See [the design blueprint](../../docs/AI_STUDIO_ARCHITECTURE.md) for the architecture, staged delivery plan, quality gates, and data privacy requirements.
