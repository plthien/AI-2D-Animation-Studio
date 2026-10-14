# P0 upstream port manifest

Target baseline: `plthien/AI-2D-Animation-Studio@7f63b95ae26942064aeba91ecc9e612e1582687c`
Authorized source: `plthien/ytb-ai-studio@393d0eb5516ac8bb8455f859b79bfc64388b128e`
Source was fetched read-only to `D:\tmp\ytb-p0-reference`; its verified `HEAD` equals the pinned SHA. The source checkout was not modified.

P0 modules were rewritten to honor the new 32-hex prefixed IDs, animation-specific artifact schema, project ownership, error envelope, immutable storage, and fresh schema. No source file was copied byte-for-byte. SHA-256 hashes below are lowercase hashes of the exact pinned source files.

| Source path | Source SHA-256 | Target path | Mode | Removed/avoided dependencies | Evidence |
|---|---|---|---|---|---|
| `app/api/errors.py` | `2119bd18e7068f31916cbbe1b94bda8dd7de9b9b416e8d9d4052936a026ded99` | `app/api/errors.py` | REWRITTEN | Removed YTB diagnostic/LLM redaction modules; P0 exposes only fixed API errors and schema paths | `tests/api/test_channels_projects.py` |
| `app/core/config.py` | `f1ae98a18b1f3238083c7fca24a373f7c797f0aca8b2889ff5b17227dc883cf0` | `app/core/config.py` | REWRITTEN | Removed YTB v3 settings, render/TTS provider toggles and legacy DB defaults | `tests/api/test_channels_projects.py` |
| `app/core/ids.py` | `ef1833ccbff4b81412a88fb900a005185e17400859aadc5b03131988d016baf3` | `app/core/ids.py` | REWRITTEN | Replaced 12-hex artifact IDs with Master Spec 32-hex prefixed IDs | `tests/platform/test_models.py`, `tests/api/test_channels_projects.py` |
| `app/core/hashing.py` | `2be86513e0d82b7866f500e68b58897fc803ab8ccad723b351d4715a4d8f22e9` | `app/core/hashing.py` | REWRITTEN | Enforced canonical UTF-8 JSON and SHA-256 domain hashes from Master Spec Â§3.1/Â§19 | `tests/api/test_channels_projects.py`, `tests/platform/test_artifacts.py` |
| `app/core/time.py` | `eeaa7273733cd1cae88fe35d692a3c1316eac05c72e625ebace110b1cba0be5f` | `app/core/time.py` | REWRITTEN | Kept UTC ISO 8601 behavior; no upstream transitive imports | `tests/platform/test_models.py` |
| `app/core/version.py` | `7af21f80d6ffbc35577b8f480589c5af955df2ef21d0f3a3dea01c8083247845` | `app/core/version.py` | REWRITTEN | Removed YTB product/version identity | `tests/api/test_channels_projects.py` |
| `app/db/__init__.py` | `0abc22df692cb0bc6ccd8488a9ff7b1b897e2ca753cee33e9b12a75af95b2dbf` | `app/db/__init__.py` | REWRITTEN | Empty package boundary; no YTB model registry | `tests/platform/test_migration.py` |
| `app/db/base.py` | `2cab48dfcf8700034b177d5e327c8e278eb653235f51189bd2b549f9a954d97f` | `app/db/base.py` | REWRITTEN | New declarative base; does not import YTB models | `tests/platform/test_migration.py` |
| `app/db/session.py` | `8f344b291cf4079f9182f496df243ac6d7d7d13e17319555a38c9c4f5eb56542` | `app/db/session.py` | REWRITTEN | Removed YTB settings profile and parent pragma adapter | `tests/platform/test_models.py`, `tests/platform/test_artifacts.py` |
| `app/db/dependencies.py` | `401f48a0961fa1f18b370cee5d65f3a2e22722dd5a741da8d1272d74b2787a2f` | `app/db/dependencies.py` | REWRITTEN | Session dependency bound to fresh platform session factory | `tests/api/test_channels_projects.py` |
| `app/db/types.py` | `f16714c525b7fd3a5237a2141ee7c70a95753ba09aba768bb8adfdb27ae138e5` | `app/db/types.py` | REWRITTEN | Canonical JSONText for new animation models; no legacy payload adapter | `tests/platform/test_models.py` |
| `app/db/sqlite_pragmas.py` | `ac211dec8eaaf3442749bfdd323c64e4572fdaffe9a7c601b695ee2ad5a7053c` | `app/db/sqlite_pragmas.py` | REWRITTEN | Retained only FK, WAL and busy timeout setup | `tests/platform/test_models.py`, migration test |
| `app/infrastructure/sqlite.py` | `90ced71258b9e4cee6f42d16887f0dbd4b8a7f559d25d6f5a017f6702dfd59a9` | `app/infrastructure/sqlite.py` | REWRITTEN | Kept parent-directory preparation only | `tests/platform/test_migration.py` |
| `app/services/artifacts.py` | `d436e565691d947b162601c13ded4585e8cc64108aa792aa51c6a654d7fe1141` | `app/services/artifacts.py` | REWRITTEN | Removed upstream artifact roles/types and YTB repository coupling | `tests/platform/test_artifacts.py` |
| `app/services/jobs.py` | `81a9506dbd8fb4cf86b409fa036a2523df6ea88002a0c6421534971845f4c0ec` | `app/services/jobs.py` | REWRITTEN | Limited to read-only projection; no YTB worker lifecycle or legacy Job model | `tests/api/test_channels_projects.py` |
| `app/platform/jobs/job_service.py` | `c2488e5cc97fb5b4d2f82fa87dd313914b10ce5f4867d8cf1bb0b47c94341ed4` | `app/platform/jobs/job_service.py` | REWRITTEN | Thin adapter to the new jobs projection | `tests/api/test_channels_projects.py` |
| `app/api/routes/system.py` | `49beb4e9af6eea1380609f935edf483c0c734b6d4980776cf246dc731c4ad521` | `app/api/routes/system.py` | REWRITTEN | Removed YTB settings and v3 health projection | `tests/api/test_channels_projects.py` |
| `app/api/routes/jobs.py` | `180b2492ee18c827967d97335c8148094e49a95e4c620844ca9cf63fb4dbd648` | `app/api/routes/jobs.py` | REWRITTEN | Removed YTB repositories and old job fields; read-only P0 job projection | `tests/api/test_channels_projects.py` |
| `app/api/routes/artifacts.py` | `bd94a836946fbeb7d763467936c7b39d72a2d8b06d225e391b192a49e39540c9` | `app/api/routes/artifacts.py` | REWRITTEN | Removed legacy artifact download/type adapters; added project-scoped metadata listing | `tests/api/test_channels_projects.py` |
| `src/layout/CockpitShell.tsx` | `193008370043cc6594b69675c5665d2f18597ce7f223c9d2a8434b4f8715a3d4` | `src/layout/AppShell.tsx` | REWRITTEN | Replaced Tailwind shell and YTB workspace context with MUI and React Router | `npm run build`, `npm test` |
| `src/layout/GlobalSidebar.tsx` | `c800927bd597c1622ed13d64cc2ec846abdb5680390c91852947cc1eabd238b7` | `src/layout/AppShell.tsx` | REWRITTEN | Removed YTB icons, app-view union and old navigation | `npm run build` |
| `src/layout/PageHeader.tsx` | `206ed7b528e44abcadb94219292e1d3e6b65a894eba732b546eeb2559bb44b42` | `src/pages/ChannelsPage.tsx`, `ProjectsPage.tsx`, `StudioPage.tsx`, `JobsPage.tsx`, `SettingsPage.tsx` | REWRITTEN | Kept page heading role; replaced styling dependencies | `npm run build` |
| `src/layout/PipelineStepper.tsx` | `02263173bd2fe25e3d94971a55554002ea6cd01e39cca798749c670ee8ad937f` | `src/pages/StudioPage.tsx` | REWRITTEN | Replaced legacy statuses and stage actions with seven backend status records | `tests/frontend/workflow.test.mjs` |
| `src/pages/ChannelsPage.tsx` | `c511738d8bfe2788ce57d3b18628a4b9d7ceed87cdf05ca51a9ae4ce659ccc69` | `src/pages/ChannelsPage.tsx` | REWRITTEN | Removed old channel model and static pages; uses persisted P0 API | `npm run build`, live HTTP smoke |
| `src/pages/ProjectsPage.tsx` | `db0893404c82c689bdbef69acc8fb80c2b5bef3bd27978d1fb9576239605fe5f` | `src/pages/ProjectsPage.tsx` | REWRITTEN | Removed legacy project pointers and old routes | `npm run build`, live HTTP smoke |
| `src/pages/StudioPage.tsx` | `5f9204cfd7e69b7ea8555860eb05a8ac6c26ed3fa8d1ffe378fb7dd98f8e1a18` | `src/pages/StudioPage.tsx` | REWRITTEN | Removed old stage list and static workflow panels | `tests/frontend/workflow.test.mjs`, live HTTP smoke |
| `src/pages/SettingsPage.tsx` | `f6ba0ec8bacfb27b923702fabc641e99a69bcb16c0fb98003649a40417cfc0a9` | `src/pages/SettingsPage.tsx` | REWRITTEN | P0-only readiness and fixed render settings | `npm run build`, live HTTP smoke |
| `src/pages/JobsPage.tsx` | `033fde9617a13e765605db5607732cc98691149656b444c257d5134d5f4ff1e6` | `src/pages/JobsPage.tsx` | REWRITTEN | Removed old worker lease fields and YTB job projection | `tests/frontend/workflow.test.mjs` |

## Explicitly excluded source modules

| Source path | Source SHA-256 | Reason |
|---|---|---|
| `app/repositories/core.py` | `a43418e15dd0e6c6aae92709bb557decfb846cfcf169002485c36cb042e91fa9` | Imports YTB SceneAsset and other legacy domain models; a fresh `ArtifactRepository` and `ProjectRepository` were written instead. |
| `app/modules/platform/artifact_loader.py` | `e828b8c5e01ecd98b03121efb2b933d1499d834386705b04ee1c66636bd10eac` | Imports YTB `/v4` script timing validation and old artifact enums; excluded. |

The upstream `requirements.txt` and `package.json` were inspected. Python dependency versions in this branch follow its pinned neutral baseline where available. React/MUI/React Query baseline versions follow its manifest; Vite is fixed to 5.4.21 and router to a security-patched 7.18.4. `package-lock.json` is newly generated for this product and does not copy the upstream lockfile.

| Source path | Source SHA-256 | Target path | Decision | Note |
|---|---|---|---|---|
| `requirements.txt` | `783c3e6479df0f501c3534adc60b221d2b896341e8841e2d501293eed42aa3e6` | `requirements.txt` | REWRITTEN | Retains pinned FastAPI/Pydantic/SQLAlchemy/Alembic/httpx/pytest/jsonschema baseline; adds `python-dotenv` for `.env` loading. |
| `package.json` | `ebd8bbb9deb220fa9400c2343b481ccd88f162f29fc81836750d39d27407d063` | `package.json` | REWRITTEN | Retains React 18/MUI 5/React Query 5/Vite 5 baseline; drops unused YTB packages and the development server script. |

The P0 Channels and Projects API/service logic is authored against the new P0 plan and Master Spec; no YTB channel/project routes or repositories were imported because those bind to the upstream model registry and old database schema.
