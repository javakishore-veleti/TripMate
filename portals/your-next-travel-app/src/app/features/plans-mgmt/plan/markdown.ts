function formatInline(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>');
}

function isTableSeparator(line: string): boolean {
  const trimmed = line.trim();
  return trimmed.includes('-') && /^\|?[\s:|-]+\|?$/.test(trimmed);
}

function isTableRow(line: string): boolean {
  const trimmed = line.trim();
  return trimmed.includes('|') && trimmed.split('|').filter(Boolean).length >= 2;
}

function cells(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => formatInline(cell.trim()));
}

export function renderMarkdown(markdown: string): string {
  const escaped = (markdown || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  const lines = escaped.split('\n');
  const html: string[] = [];
  let inList = false;
  let listTag = 'ul';
  let tableRows: string[][] = [];

  const closeList = () => {
    if (inList) {
      html.push(`</${listTag}>`);
      inList = false;
    }
  };

  const flushTable = () => {
    if (!tableRows.length) {
      return;
    }
    const [header, ...body] = tableRows;
    html.push('<div class="itinerary-table-wrap"><table class="itinerary-table">');
    html.push('<thead><tr>');
    for (const cell of header) {
      html.push(`<th>${cell}</th>`);
    }
    html.push('</tr></thead><tbody>');
    for (const row of body) {
      html.push('<tr>');
      for (const cell of row) {
        html.push(`<td>${cell}</td>`);
      }
      html.push('</tr>');
    }
    html.push('</tbody></table></div>');
    tableRows = [];
  };

  const openList = (tag: 'ul' | 'ol') => {
    if (inList && listTag !== tag) {
      closeList();
    }
    if (!inList) {
      listTag = tag;
      html.push(`<${tag}>`);
      inList = true;
    }
  };

  for (const raw of lines) {
    const line = raw.replace(/\r$/, '');
    if (isTableRow(line) && !isTableSeparator(line)) {
      closeList();
      tableRows.push(cells(line));
      continue;
    }
    if (isTableSeparator(line) && tableRows.length) {
      continue;
    }
    flushTable();

    const item = formatInline(line);
    const numbered = item.match(/^(\d+)\.\s+(.*)$/);
    if (item.startsWith('### ')) {
      closeList();
      html.push(`<h3>${item.slice(4)}</h3>`);
    } else if (item.startsWith('## ')) {
      closeList();
      html.push(`<h2>${item.slice(3)}</h2>`);
    } else if (item.startsWith('# ')) {
      closeList();
      html.push(`<h1>${item.slice(2)}</h1>`);
    } else if (/^[-*]{3,}$/.test(item.trim()) || item.trim() === '---') {
      closeList();
      html.push('<hr />');
    } else if (item.startsWith('- ') || item.startsWith('* ')) {
      openList('ul');
      html.push(`<li>${item.slice(2)}</li>`);
    } else if (numbered) {
      openList('ol');
      html.push(`<li>${numbered[2]}</li>`);
    } else if (!item.trim()) {
      closeList();
    } else {
      closeList();
      html.push(`<p>${item}</p>`);
    }
  }
  flushTable();
  closeList();
  return html.join('');
}

export function travelAnswer(
  result: { answer?: string; itinerary?: string; final_response?: string } | undefined,
  prompt = '',
): string {
  const answer = (result?.answer || result?.itinerary || result?.final_response || '').trim();
  if (!answer || (prompt && answer === prompt)) {
    return '';
  }
  return answer;
}
