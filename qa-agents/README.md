# qa-agents

Reusable Claude Code subagents for web QA automation work: exploring live
pages, writing Selenium/pytest coverage, hunting edge cases and security
issues, and triaging test failures without papering over real bugs.

These were distilled from a multi-week Selenium/pytest project (a React
e-commerce staging site) where the same workflow kept proving out: explore
the live page first, never guess selectors, wait properly instead of
sleeping, and carefully separate "my test is wrong", "the environment
hiccuped", and "this is a real product bug" before deciding how to react
to a failure.

## Agents

- **qa-test-writer** — given a page/feature, explores it live, builds
  Page Object Model code, and writes comprehensive pytest coverage
  (happy path, boundaries, negative/malformed input). Refuses to
  perform irreversible actions (real orders, account deletion) without
  explicit confirmation.
- **qa-bug-hunter** — probes a feature for edge cases and real bugs
  without necessarily building a permanent suite; reports findings with
  concrete repro steps and an honest confirmed/by-design/inconclusive
  verdict.
- **qa-regression-runner** — runs an existing suite, triages failures
  into infra noise / race condition / wrong test assumption / real
  product bug / shared-state ordering issue, and fixes the actual
  category rather than adding retries until it's green.

## Using these in another project

Copy the `.claude/agents/` folder into the target project's root (or into
your global `~/.claude/agents/` to make them available everywhere), then
invoke by name — e.g. "use qa-test-writer to cover the checkout page" or
just let Claude Code pick them up automatically when a task matches their
description.

These agents assume the target project already has:
- A Selenium (or similar) driver fixture and basic navigation/auth helpers
- A `pages/`-style Page Object module and a `tests/`-style pytest suite

They adapt to whatever conventions already exist in that project (fixture
names, marker patterns, wait helpers) rather than imposing their own —
see each agent's "explore the existing code first" step.

## Design principles behind these agents

1. **Never guess a selector or a default value — verify it live.** A
   throwaway exploration script that dumps real DOM state beats an
   assumption every time.
2. **A wait fixes a race condition; a longer sleep just makes it rarer.**
   Any element lookup right after a click or navigation in a
   client-rendered app needs an explicit `WebDriverWait`.
3. **Distinguish "my test is wrong" from "the site is wrong" from "the
   environment hiccuped" before reacting.** Each has a different correct
   fix, and conflating them either hides real bugs or wastes time chasing
   fake ones.
4. **A failing test that documents a real, unfixed bug should stay
   red, on purpose, with a comment explaining why** — not get quietly
   adjusted to pass.
5. **Never take an irreversible action on shared/live state to test
   something**, unless it's explicitly approved and cleanly revertible,
   and the revert is actually verified afterward, not assumed.
