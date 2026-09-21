# Ramrattan Network Tools UX Guidelines

These guidelines establish the common visual and interaction system shared by
IP Scanner and Speedtest Monitor.  Product-specific workflows may differ, but
the family identity and core interaction patterns must remain consistent.

## Product identity

- Use `RAMRATTAN NETWORK TOOLS` as the header eyebrow.
- Use the Ramrattan shield logo at the left of the product title.
- Use a short, plain-language product name and a one-sentence value statement.
- Use `Ramrattan <Product Name>` in browser titles, installers, and footers.
- Keep the Help control in the upper-right of the hero on every primary page.

## Core palette

| Role | Value | Usage |
| --- | --- | --- |
| Deep navy | `#0D2942` | Hero gradient start and strong depth |
| Primary navy | `#173F63` | Primary actions, active controls, headings |
| Action blue | `#2F78B8` | Hover states, links, section eyebrows |
| Pale blue | `#EAF3FA` | Informational callouts and selected tags |
| Header blue | `#9FC8E8` | Hero eyebrow |
| Page background | `#F3F7FA` | Application canvas |
| Surface | `#FFFFFF` | Cards, tables, Help panel |
| Primary text | `#17232E` | Headings and body text |
| Muted text | `#5E6C78` | Supporting copy and captions |
| Border | `#D6E0E8` | Card, table, and control borders |

The hero uses a 135-degree gradient from deep navy to primary navy.  New
colours require an explicit accessibility and family-consistency review.

## Layout and components

- Constrain primary content to 1,180 pixels and centre it on the page.
- Use a 20-pixel hero radius and 18-pixel card radius.
- Use generous vertical spacing to separate tasks into readable sections.
- Start each major section with a blue uppercase eyebrow, a clear heading, and
  one optional explanatory sentence.
- Use white cards with subtle navy shadows for controls, metrics, and tables.
- Use icons to reinforce text labels, never as the only meaning for a critical
  action.
- Keep destructive actions visually separate from primary actions.

## Help pattern

- The question-mark control opens a right-side Help panel.
- Help remains available without navigating away or losing page context.
- Help content uses task-based cards: operate, understand, privacy, and
  troubleshooting.
- Informational reminders use pale blue with a blue left border.
- Escape, the close control, and selecting the background scrim close Help.

## Interaction guidelines

- Every long-running action must display a plain-language status and disable
  conflicting controls.
- Empty states must explain why the area is empty and identify the next action.
- Errors must explain what failed without exposing internal stack traces.
- Confirm destructive actions such as clearing history.
- Preserve local data during application upgrades and routine uninstallation
  unless the user explicitly requests removal.

## Accessibility and responsive behavior

- Maintain keyboard-visible focus on every interactive control.
- Use semantic headings, buttons, tables, status regions, and accessible names.
- Maintain readable colour contrast and do not rely on colour alone.
- Honour reduced-motion preferences.
- On narrow screens, stack actions and reduce the hero and logo dimensions.
- Keep horizontal scrolling inside wide data tables rather than the full page.
- Keep sorting on the header label and column resizing on a distinct divider so
  the two interactions cannot be confused.
- Provide keyboard resizing, a documented reset action, sensible minimum
  widths, and local persistence whenever users may resize a table.
- Pair chart colours with labels, icons, counts, and hover metrics so colour is
  never the only carrier of meaning.

## Content style

- Use concise, action-oriented labels and familiar language.
- Explain technical concepts in Help rather than crowding the primary screen.
- State clearly that data is local and that network scans require authorization.
- Do not describe planned or placeholder capabilities as available features.
