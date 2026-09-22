/**
 * LLM output sometimes collapses markdown tables onto a single line, e.g.:
 *   `| A | B | |---|---| | 1 | 2 |`
 * which renders as a plain paragraph instead of a table.
 *
 * Re-insert row breaks and proper paragraph spacing so CommonMark + remark-gfm can parse the table:
 * - header | rule-row junction:  `... | Revoked | |---|---|` → newline before `|---`
 * - collapsed row junctions:     `| 0 | | FinTech |`         → newline between rows
 * - ensure blank lines before and after table blocks for strict CommonMark parsing
 */
export function normalizeMarkdownTables(md: string): string {
  if (!md || !md.includes('|') || !/-{2,}/.test(md)) return md
  let out = md

  // 1. Header -> rule-row junction when collapsed onto one line:
  // `Status | |-----------|---------|` -> `Status |\n|-----------|---------|`
  out = out.replace(/\s\|\s\|(?=\s*:?-{2,})/g, ' |\n|')

  // 2. Row-to-row junctions:
  // `| Active | | ABC123 |` or `|---| | ABC124 |` -> `| Active |\n| ABC123 |`
  out = out.replace(/\|([ \t]+)\|(?=[ \t]*[^\s|])/g, '|\n|')

  // 3. Ensure blank line before table if collapsed into preceding non-table text:
  // `...sorted by expiry date: | Cert ID |` -> `...sorted by expiry date:\n\n| Cert ID |`
  out = out.replace(/([^\n|])\s*(\|(?:\s*[^|\n]+\s*\|)+[ \t]*\n[ \t]*\|(?:\s*:?-{2,}:?\s*\|)+)/g, '$1\n\n$2')

  // 4. Ensure blank line after last table row if followed immediately by non-table text:
  // `| Active |\nKey highlights:` -> `| Active |\n\nKey highlights:`
  out = out.replace(/(\|(?:[^\n|]+\|)+)\n(?!\s*(?:\||\n))([^\n])/g, '$1\n\n$2')

  return out
}