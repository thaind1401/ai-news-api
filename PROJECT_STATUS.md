# Project Status Dashboard (AI Signals API)

Last updated: 2026-03-16

Status legend: DONE / IN_PROGRESS / TODO

## 1) Summary

| Track | DONE | WIP | TODO |
| --- | ---: | ---: | ---: |
| ProductPlan (9) | 3 | 3 | 3 |
| Roadmap (10w) | 2 | 3 | 5 |

| Key | Value |
| --- | --- |
| Phase | Ingestion + API + Enrichment baseline |
| Current stage | Stage 2 (IN_PROGRESS) |
| Next stage | Stage 3 |
| Main goal | Search API thật |
| Main gap | Retrieval + RAG + Digest + User |
| Stage plan | [AI_LEARNING_APPLY_PLAN.md](AI_LEARNING_APPLY_PLAN.md) |

## 1.1) AI Stage tracker (2 -> 6)

| Stage | Name | Status | Current focus |
| --- | --- | --- | --- |
| 2 | LLM + Prompt Engineering | IN_PROGRESS | LLM structured enrichment + output schema |
| 3 | RAG + Vector DB | TODO | Embeddings + hybrid search |
| 4 | Agents + Tool Use | TODO | Grounded assistant + tool orchestration |
| 5 | AI System Architecture | TODO | Runtime boundaries + observability |
| 6 | Deployment + Automation + Integration | TODO | CI/CD + jobs + monitoring |

## 2) Kanban board

| ID | Lane | Status | Task |
| --- | --- | --- | --- |
| N1 | NOW | TODO | Search API v1 |
| N2 | NOW | TODO | Search output schema |
| N3 | NOW | TODO | Sync ROADMAP checkboxes |
| X1 | NEXT | TODO | Async enrichment worker |
| X2 | NEXT | TODO | Digest API v1 |
| X3 | NEXT | TODO | User API nền |
| L1 | LATER | TODO | Embeddings + retrieval |
| L2 | LATER | TODO | Chat RAG grounded |
| L3 | LATER | TODO | Alert + personalization |

| ID | Owner | ETA | Note |
| --- | --- | --- | --- |
| N1 | Thai | This week | Priority #1 |
| N2 | Thai | This week | Reuse cho chat |
| N3 | Thai | This week | Docs sync |
| X1 | Thai | Next | Scale-ready |
| X2 | Thai | Next | Daily brief MVP |
| X3 | Thai | Next | Tuần 8-9 |
| L1 | Thai | Later | Tuần 6 |
| L2 | Thai | Later | Tuần 7 |
| L3 | Thai | Later | Tuần 8-10 |

## 3) Blockers / risks

| ID | Type | Level | Status | Item |
| --- | --- | --- | --- | --- |
| B1 | Blocker | High | Open | Search/Digest còn 501 |
| R1 | Risk | High | Open | Chưa có retrieval pipeline |
| R2 | Risk | Med | Open | Nguồn crawl biến động |

| ID | Action |
| --- | --- |
| B1 | Implement Search + Digest API thật |
| R1 | Làm embeddings + retrieval tuần 6 |
| R2 | Theo dõi source_fetch_runs định kỳ |

## 4) Recent updates

| Date | ID | Update |
| --- | --- | --- |
| 2026-03-16 | U4 | Added stage tracker + link to learning apply plan |
| 2026-03-16 | U1 | Chat route -> /api/v1/chat |
| 2026-03-16 | U2 | Internal auth test 401/403/200 |
| 2026-03-16 | U3 | Full architecture migration done |

## 5) Implementation snapshot

| ID | Area | Status |
| --- | --- | --- |
| I1 | Signals API | DONE |
| I2 | Ingestion pipeline | DONE |
| I3 | Enrichment baseline | IN_PROGRESS |
| I4 | Internal jobs auth | DONE |
| I5 | Search API | TODO |
| I6 | Digest API | TODO |
| I7 | User API | TODO |
| I8 | AI retrieval/RAG | TODO |

| ID | Ref |
| --- | --- |
| I1 | [app/api/routers/signals.py](app/api/routers/signals.py) |
| I2 | [app/ingestion/workers/pipeline.py](app/ingestion/workers/pipeline.py) |
| I3 | [app/services/ingestion_service.py](app/services/ingestion_service.py) |
| I4 | [app/api/routers/internal_jobs.py](app/api/routers/internal_jobs.py) |
| I5 | [app/api/routers/search.py](app/api/routers/search.py) |
| I6 | [app/api/routers/digests.py](app/api/routers/digests.py) |
| I7 | [app/api/routers/users.py](app/api/routers/users.py) |
| I8 | [app/ai/](app/ai/) |

## 6) Session log

| Date | Done | WIP | Blocked | Next |
| --- | --- | --- | --- | --- |
| 2026-03-16 | U1,U2,U3,U4 | N1 | B1 | N1,N3 |

## 7) Update rules

| Rule | Value |
| --- | --- |
| Frequency | Sau mỗi phiên lớn |
| Unit | 1 task = 1 dòng |
| Status | DONE / IN_PROGRESS / TODO |
| Log | Mỗi phiên thêm 1 dòng |

