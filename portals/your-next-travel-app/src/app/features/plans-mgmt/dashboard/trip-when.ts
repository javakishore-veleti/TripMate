import { TravelRequestRecord } from '../../../core/models/api.models';

function parseDate(raw?: string): Date | null {
  if (!raw) {
    return null;
  }
  const date = new Date(raw);
  return Number.isNaN(date.getTime()) ? null : date;
}

function firstWeekday(year: number, month: number, weekday: number): Date {
  const start = new Date(year, month, 1);
  const delta = (weekday - start.getDay() + 7) % 7;
  return new Date(year, month, 1 + delta);
}

function nthWeekday(year: number, month: number, weekday: number, nth: number): Date {
  const first = firstWeekday(year, month, weekday);
  return new Date(year, month, first.getDate() + (nth - 1) * 7);
}

function upcomingYear(from: Date, month: number, day: number): number {
  const candidate = new Date(from.getFullYear(), month, day);
  return candidate < new Date(from.getFullYear(), from.getMonth(), from.getDate())
    ? from.getFullYear() + 1
    : from.getFullYear();
}

function addDays(start: Date, count: number): Date[] {
  const days: Date[] = [];
  for (let i = 0; i < Math.max(1, count); i += 1) {
    days.push(new Date(start.getFullYear(), start.getMonth(), start.getDate() + i));
  }
  return days;
}

function durationDays(record: TravelRequestRecord): number {
  const constraints = record.result?.trip_constraints || {};
  const raw = String(
    constraints.duration ||
      record.prompt ||
      record.result?.final_response ||
      record.result?.answer ||
      '',
  );
  const range = raw.match(/(\d+)\s*[-–to]+\s*(\d+)\s*-?\s*days?/i);
  if (range) {
    return Number(range[2]);
  }
  const single = raw.match(/(\d+)\s*-?\s*days?/i);
  return single ? Number(single[1]) : 1;
}

export function plannedAt(record: TravelRequestRecord): Date | null {
  const fromFields = parseDate(record.created_at) || parseDate(record.updated_at);
  if (fromFields) {
    return fromFields;
  }
  const stamp = record.thread_id.match(/^(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})/);
  if (!stamp) {
    return null;
  }
  return new Date(
    Number(stamp[1]),
    Number(stamp[2]) - 1,
    Number(stamp[3]),
    Number(stamp[4]),
    Number(stamp[5]),
    Number(stamp[6]),
  );
}

function knownEventStart(prompt: string, from: Date): Date | null {
  const text = prompt.toLowerCase();
  if (/new york city marathon|nyc marathon|new york marathon/.test(text)) {
    const year = upcomingYear(from, 10, 7);
    return firstWeekday(year, 10, 0);
  }
  if (/thanksgiving/.test(text)) {
    const year = upcomingYear(from, 10, 20);
    return nthWeekday(year, 10, 4, 4);
  }
  if (/new year/.test(text)) {
    return new Date(from.getFullYear() + (from.getMonth() === 0 && from.getDate() < 2 ? 0 : 1), 0, 1);
  }
  return null;
}

function constraintStart(record: TravelRequestRecord): Date | null {
  const constraints = record.result?.trip_constraints || {};
  return (
    parseDate(String(constraints.start_date || constraints.date || constraints.when || ''))
  );
}

export function tripDates(record: TravelRequestRecord): Date[] {
  const planned = plannedAt(record) || new Date();
  const start = constraintStart(record) || knownEventStart(record.prompt || '', planned);
  if (!start) {
    return plannedAt(record) ? addDays(planned, 1) : [];
  }
  return addDays(start, durationDays(record));
}

export function formatDay(date: Date): string {
  return date.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
}

export function formatDateTime(date: Date): string {
  return date.toLocaleString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function tripWindowLabel(record: TravelRequestRecord): string {
  const days = tripDates(record);
  if (!days.length) {
    return '';
  }
  if (days.length === 1) {
    return formatDay(days[0]);
  }
  return `${formatDay(days[0])} – ${formatDay(days[days.length - 1])}`;
}

export function calendarKey(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
