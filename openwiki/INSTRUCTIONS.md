# OpenWiki Repository Documentation Mandate (Bilingual EN + KO & Business Context)

All OpenWiki documentation runs (`init`, `chat`, and scheduled `--update`) in this repository MUST obey the following rules strictly:

1. **Mandatory Bilingual Output (English First, Then Korean)**:
   - Every wiki page (`openwiki/**/*.md`, excluding generated `index.md`) MUST contain complete, synchronized documentation in **both English and Korean**.
   - Structure every section, page `title` (`<English Title> / <한국어 제목>`), `description` (`<English summary> <한국어 요약>`), table, and prose block with **English first, immediately followed by the equivalent Korean translation**.
   - Keep code identifiers, file paths, CLI commands, URLs, and fenced code blocks unchanged across both languages.
   - Always propagate this bilingual requirement AND the relative-link requirement into every page job's `instructions` array during planning.

2. **Business Role & Value Proposition First**:
   - `openwiki/quickstart.md` (and any introductory overview page) MUST open with a dedicated **`## Business Role & Value Proposition / 비즈니스 역할 및 가치`** section explaining this repository's commercial, GTM, and regulatory role in the ZeroStreet (`주식회사 제로스트리트`) B2A ecosystem—before diving into modules and schemas.

3. **Relative Markdown Links Only**:
   - Every internal link to another OpenWiki page or repository file MUST be a relative path (e.g., `./architecture/pit-and-multimodal-contracts.md`, `../quickstart.md`, `../src/zerostreet_schema/pit.py`).
   - NEVER use root-absolute `/openwiki/...` links in Markdown destinations.

4. **Strict Repository Grounding & Claims**:
   - Cite every Claim strictly with `repo://<path>#L<start>-L<end>` verified against current files, and keep code identifiers consistent across English and Korean prose.
