# IP Scanner Documentation

This directory is the documentation and repository-wiki source of truth for IP
Scanner.  The documents separate verified history, current behavior, product
standards, and future work so that planned capabilities are never mistaken for
available features.

## Start here

| Document | Purpose | Audience |
| --- | --- | --- |
| [Current Baseline](Current-Baseline.md) | Defines the accepted functional checkpoint and its acceptance evidence | Owners, developers, testers |
| [In-application Help](../src/network_scanner/ui/index.html) | Provides operating and troubleshooting guidance without leaving the application | Operators |
| [Discovery Confidence](Discovery-Confidence.md) | Explains evidence, confidence, unknown values, and artifact controls | Operators, testers |
| [UX Guidelines](UX-Guidelines.md) | Defines the shared Ramrattan Network Tools visual and interaction system | Designers, developers |
| [Third-Party Notices](Third-Party-Notices.md) | Records the vendor lookup package, license, and local OUI data source | Owners, maintainers |
| [Kanban](KANBAN.md) | Tracks completed, active, next, later, and blocked work | Project team |
| [Roadmap](ROADMAP.md) | Records project origination through the current checkpoint and future stages | Owners, project team |
| [Recovery Baseline](Recovery-Baseline.md) | Audits the inherited `v1.07` source and records recovery decisions | Maintainers |

## Status language

- **Available** means implemented in source and exercised by automated or
  documented manual verification.
- **Accepted baseline** means suitable as the protected starting point for the
  next delivery stage.
- **Source release** means the tested Python application is tagged and
  published without standalone desktop installers.
- **In review** means implemented or documented but still awaiting a named
  acceptance gate.
- **Planned** means sequenced on the Kanban or roadmap and not yet available.
- **Historical claim** means described by an earlier changelog or README but not
  necessarily present in the audited source.

## Updating the record

When behavior changes, update the application Help, Current Baseline, Kanban,
Roadmap, README, and Changelog as applicable in the same pull request.  Move a
card to Done only when its stated acceptance evidence exists.  Preserve the
current `main` baseline, release tag `v1.0.0`, and historical `v1.07` tag.
Implement material changes on focused branches and merge them only after the
required approval and verification gates pass.
