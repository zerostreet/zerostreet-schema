<!-- OPENWIKI:START -->

## OpenWiki

This repository has a generated `openwiki/` evidence index. It is optional just-in-time context, not required startup reading.

- Do not enumerate, preload, or search wikis at task start. Use retrieval when the user asks for it, when unfamiliar architecture or dependency behavior materially affects the task, or when source inspection leaves an important uncertainty. Stop once the question is grounded.
- When those conditions apply and OpenWiki retrieval tools are available, use `openwiki_search` for just-in-time context and `openwiki_read` for the relevant complete sections. If search returns `workspace_required`, ask which listed workspace to use and retry with its ID.
- Use `openwiki_list_workspaces` or `openwiki_list_wikis` when workspace membership itself needs to be discovered.
- If the retrieval tools are unavailable, read `openwiki/quickstart.md` and follow its links to the relevant pages.
- Treat source code and tests as authoritative. A brief's unknowns and review items are verification gaps, not automatic requirements.
- Prefer the narrowest quiet validation that proves the changed behavior. Preserve complete failure output.

The scheduled OpenWiki GitHub Actions workflow refreshes the repository wiki. Do not hand-edit generated OpenWiki pages unless explicitly asked; prefer updating source code/docs and letting OpenWiki regenerate.

<!-- OPENWIKI:END -->

## Repository Documentation & Bilingual Standards / 문서 및 다국어 작성 규칙

- **Python Docstrings (`src/**/*.py`)**: Every module, public class, and public function/method MUST carry a bilingual docstring written with **English first, immediately followed by the Korean equivalent** (keep lines `<= 100` chars).
- **README & OpenWiki Documentation**: Keep `openwiki/INSTRUCTIONS.md` authoritative. Every `README.md` and `openwiki/quickstart.md` MUST open with the repository's **Business Role & Value Proposition / 비즈니스 역할 및 가치**, and all OpenWiki pages MUST be written bilingually (English first, then Korean) using relative internal Markdown links only.
