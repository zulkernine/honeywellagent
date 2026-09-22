/**
 * LLM output sometimes collapses markdown tables onto a single line, e.g.:
 *   `| A | B | |---|---| | 1 | 2 |`
 * which renders as a plain paragraph instead of a table.
 *
 * Re-insert row breaks so CommonMark can parse the table:
 * - header | rule-row junction:  `... | Revoked | |---|---|` → newline before `|---`
 * - collapsed row junctions:     `| 0 | | FinTech |`         → newline between rows
 * Only runs when a table rule (`|---`) exists in the text, and proper
 * multi-line tables are untouched (their junctions contain newlines, not spaces).
 */
export function normalizeMarkdownTables(md: string): string {
  if (!md.includes('|') || !/-{2,}/.test(md)) return md
  let out = md
  // `Revoked | |---|---|`  →  `Revoked |\n|---|---|`
  out = out.replace(/\s\|\s\|(?=\s*:?-{2,})/g, ' |\n|')
  // `| 0 | | FinTech Corp |` or `|---| | Acme Corp |`  →  newline between rows
  out = out.replace(/\|([ \t]+)\|(?=[ \t]*[^\s|])/g, '|\n|')
  return out
}