# Provenance and implementation scope

Upstream: https://github.com/MahendharReddyM/Codex-agentic-ai-url-shortner

Baseline: `b4de9e1` (original history is available in the upstream repository).
License: MIT; the original LICENSE is unchanged.

This is an attributed adaptation, not a claim that the upstream code was authored here.
This repository imports the implementation in nine component-focused commits through the
GitHub API. These import commits do not represent original authorship of the upstream code.
Local additions personalize setup/documentation, configure portable test mocking, and add
a repeatable HTTP smoke check and CI scenarios with validation evidence.

## Retained implementation

Java 21 / Spring Boot REST APIs, expiry, idempotency, privacy-reduced analytics,
rate limiting, graph orchestration, governance, exact-hash approvals, isolated patching,
model adapters, fixed build validation, bounded repair, rollback, persistence, audit
verification, reliability metrics, OpenAPI, Docker Compose and CI quality gates.

## Demonstration boundaries

The deterministic provider generates a small requirement-lineage Java type and test;
it demonstrates the execution mechanism, not arbitrary feature implementation.
The real OpenAI provider requires your own API key and independent review of its output.
Workflow unit tests inject build evidence; the HTTP smoke check exercises actual Maven
execution when run with engineering scenarios enabled.

URL links, analytics and the compatibility orchestration API use in-memory storage.
Engineering run metadata can use files or PostgreSQL. This does not make all application
state durable. Container workspaces use temporary storage in the reference Compose setup.
Use persistent workspace volumes and a hardened build sandbox before production use.

The assignment PDF is intentionally not committed because it is marked internal.
