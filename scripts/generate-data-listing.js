#!/usr/bin/env node
// Parses seed-expanded.sql and generates a markdown data listing
const fs = require('fs');
const path = require('path');

const seedPath = path.join(__dirname, '..', 'database', 'seed-expanded.sql');
const outPath = path.join(__dirname, '..', 'docs', 'data-listing.md');
const sql = fs.readFileSync(seedPath, 'utf8');

// ---- Helpers ----
function escapeMarkdown(s) {
  if (!s) return '';
  return s.replace(/\|/g, '\\|').replace(/\n/g, ' ');
}

function truncate(s, max = 80) {
  if (!s) return '';
  return s.length > max ? s.slice(0, max - 1) + '…' : s;
}

// ---- Parse INSERT statements ----
// Matches: INSERT INTO tablename (...) VALUES (...)
// Handles multi-row inserts: VALUES (...), (...), (...)
function parseInserts(sql, tableName) {
  const rows = [];
  // Find all INSERT INTO <tableName> blocks
  const pattern = new RegExp(
    `INSERT\\s+INTO\\s+${tableName}\\s*\\(([^)]+)\\)\\s*VALUES\\s*([\\s\\S]*?)(?=;\\s*(?:--|INSERT|CREATE|$))`,
    'gi'
  );

  let match;
  while ((match = pattern.exec(sql)) !== null) {
    const columns = match[1].split(',').map(c => c.trim());
    const valuesBlock = match[2];

    // Parse each row tuple — handle nested parens, escaped quotes
    let depth = 0;
    let current = '';
    let inString = false;
    let escaped = false;

    for (let i = 0; i < valuesBlock.length; i++) {
      const ch = valuesBlock[i];

      if (escaped) {
        current += ch;
        escaped = false;
        continue;
      }

      if (ch === '\\') {
        current += ch;
        escaped = true;
        continue;
      }

      if (ch === "'" && !escaped) {
        inString = !inString;
        current += ch;
        continue;
      }

      if (inString) {
        current += ch;
        continue;
      }

      if (ch === '(') {
        if (depth === 0) {
          current = '';
        } else {
          current += ch;
        }
        depth++;
      } else if (ch === ')') {
        depth--;
        if (depth === 0) {
          // Parse this row
          const values = parseRowValues(current);
          const row = {};
          columns.forEach((col, idx) => {
            row[col] = values[idx] !== undefined ? values[idx] : null;
          });
          rows.push(row);
        } else {
          current += ch;
        }
      } else {
        if (depth > 0) current += ch;
      }
    }
  }
  return rows;
}

function parseRowValues(raw) {
  const values = [];
  let current = '';
  let inString = false;
  let i = 0;

  while (i < raw.length) {
    const ch = raw[i];

    if (inString) {
      if (ch === "'" && i + 1 < raw.length && raw[i + 1] === "'") {
        current += "'";
        i += 2;
        continue;
      }
      if (ch === "'") {
        inString = false;
        i++;
        continue;
      }
      current += ch;
      i++;
    } else {
      if (ch === "'") {
        inString = true;
        i++;
      } else if (ch === ',') {
        values.push(current.trim() === 'NULL' ? null : current.trim());
        current = '';
        i++;
      } else {
        current += ch;
        i++;
      }
    }
  }
  values.push(current.trim() === 'NULL' ? null : current.trim());
  return values;
}

// ---- Parse all tables ----
const cases = parseInserts(sql, 'cases');
const people = parseInserts(sql, 'people');
const timelineEvents = parseInserts(sql, 'timeline_events');
const statements = parseInserts(sql, 'statements');
const discrepancies = parseInserts(sql, 'discrepancies');

// Assign synthetic person_ids (IDENTITY starts at 1)
people.forEach((p, i) => { p._person_id = i + 1; });

// ---- Generate Markdown ----
const lines = [];
const add = (s = '') => lines.push(s);

add('# Data Listing — DSS Legal Case Agent');
add();
add(`Generated: ${new Date().toISOString().split('T')[0]}`);
add();
add('## Summary');
add();
add('| Table | Rows |');
add('|-------|------|');
add(`| cases | ${cases.length} |`);
add(`| people | ${people.length} |`);
add(`| timeline_events | ${timelineEvents.length} |`);
add(`| statements | ${statements.length} |`);
add(`| discrepancies | ${discrepancies.length} |`);
add();

// ---- Cases ----
add('## Cases');
add();
add('| # | Case ID | Title | Type | Circuit | County | Filed | Status |');
add('|---|---------|-------|------|---------|--------|-------|--------|');
cases.forEach((c, i) => {
  add(`| ${i + 1} | ${c.case_id} | ${escapeMarkdown(truncate(c.case_title, 50))} | ${c.case_type} | ${truncate(c.circuit, 30)} | ${c.county} | ${c.filed_date} | ${c.status} |`);
});
add();

// ---- People (grouped by case) ----
add('## People');
add();
add('| ID | Case ID | Name | Role | Relationship |');
add('|----|---------|------|------|-------------|');
people.forEach((p) => {
  add(`| ${p._person_id} | ${p.case_id} | ${escapeMarkdown(p.full_name)} | ${p.role} | ${escapeMarkdown(truncate(p.relationship, 60))} |`);
});
add();

// ---- Timeline Events (summary) ----
add('## Timeline Events');
add();
add('| # | Case ID | Date | Time | Type | Description |');
add('|---|---------|------|------|------|-------------|');
timelineEvents.forEach((e, i) => {
  add(`| ${i + 1} | ${e.case_id} | ${e.event_date} | ${e.event_time || ''} | ${e.event_type} | ${escapeMarkdown(truncate(e.description, 100))} |`);
});
add();

// ---- Statements (summary) ----
add('## Statements');
add();
add('| # | Case ID | Person ID | Date | Made To | Statement |');
add('|---|---------|-----------|------|---------|-----------|');
statements.forEach((s, i) => {
  add(`| ${i + 1} | ${s.case_id} | ${s.person_id} | ${s.statement_date || ''} | ${s.made_to} | ${escapeMarkdown(truncate(s.statement_text, 100))} |`);
});
add();

// ---- Discrepancies (summary) ----
add('## Discrepancies');
add();
add('| # | Case ID | Topic | Person A | Person B | Contradicted By |');
add('|---|---------|-------|----------|----------|-----------------|');
discrepancies.forEach((d, i) => {
  add(`| ${i + 1} | ${d.case_id} | ${escapeMarkdown(truncate(d.topic, 50))} | ID ${d.person_a_id} | ID ${d.person_b_id} | ${escapeMarkdown(truncate(d.contradicted_by, 80))} |`);
});
add();

fs.writeFileSync(outPath, lines.join('\n'), 'utf8');
console.log(`Written ${outPath}`);
console.log(`  Cases: ${cases.length}, People: ${people.length}, Events: ${timelineEvents.length}, Statements: ${statements.length}, Discrepancies: ${discrepancies.length}`);
