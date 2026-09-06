import { Destination, DESTINATION_GROUPS } from '../../travel-search/destinations';
import { TravelRequestRecord } from '../../../core/models/api.models';

export interface TripStory {
  title: string;
  country: string;
  vibe: string;
  image: string;
  line: string;
  when: string;
  status: string;
  cta: string;
  href: string[];
}

const FALLBACK: Destination = {
  name: 'Open road',
  country: '',
  vibe: 'The trip is taking shape',
  image: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1200&q=70',
};

const COUNTRY_HINTS: Record<string, string> = {
  japan: 'Japan',
  japanese: 'Japan',
  italy: 'Italy',
  italian: 'Italy',
  france: 'France',
  french: 'France',
  spain: 'Spain',
  spanish: 'Spain',
  greece: 'Greece',
  greek: 'Greece',
  thailand: 'Thailand',
  thai: 'Thailand',
  indonesia: 'Indonesia',
  bali: 'Indonesia',
  vietnam: 'Vietnam',
  india: 'India',
  indian: 'India',
  nepal: 'Nepal',
  morocco: 'Morocco',
  egypt: 'Egypt',
  kenya: 'Kenya',
  tanzania: 'Tanzania',
  portugal: 'Portugal',
  netherlands: 'Netherlands',
  switzerland: 'Switzerland',
  iceland: 'Iceland',
  norway: 'Norway',
  canada: 'Canada',
  mexico: 'Mexico',
  brazil: 'Brazil',
  peru: 'Peru',
  argentina: 'Argentina',
  australia: 'Australia',
  'new zealand': 'New Zealand',
  england: 'UK',
  scotland: 'UK',
  britain: 'UK',
  uk: 'UK',
  usa: 'USA',
  america: 'USA',
  hawaii: 'USA',
};

function allPlaces(): Destination[] {
  return DESTINATION_GROUPS.flatMap((group) => group.places);
}

export function placeByName(name: string): Destination | undefined {
  const needle = name.toLowerCase();
  return allPlaces()
    .filter((place) => place.name.toLowerCase() === needle || place.name.toLowerCase().includes(needle))
    .sort((a, b) => a.name.length - b.name.length)[0];
}

export function placeForCountry(country: string): Destination {
  return allPlaces().find((place) => place.country.toLowerCase() === country.toLowerCase()) ?? FALLBACK;
}

export function photoForPlace(placeName: string, country: string, fallback?: string): string {
  return placeByName(placeName)?.image || placeForCountry(country).image || fallback || FALLBACK.image;
}

function matchPlace(prompt: string): { place: Destination; title: string; country: string } {
  const text = prompt.toLowerCase();
  const places = allPlaces();

  const named = places
    .filter((place) => text.includes(place.name.toLowerCase()))
    .sort((a, b) => b.name.length - a.name.length)[0];
  if (named) {
    return { place: named, title: named.name, country: named.country };
  }

  const hinted = Object.entries(COUNTRY_HINTS).find(([hint]) => {
    return new RegExp(`\\b${hint}\\b`, 'i').test(prompt);
  });
  if (hinted) {
    const country = hinted[1];
    const place = places.find((item) => item.country === country) ?? FALLBACK;
    return { place, title: country === 'UK' ? 'United Kingdom' : country, country };
  }

  const byCountry = places.find((place) => text.includes(place.country.toLowerCase()));
  if (byCountry) {
    return { place: byCountry, title: byCountry.country, country: byCountry.country };
  }

  return { place: FALLBACK, title: 'A trip in progress', country: '' };
}

function duration(prompt: string): string {
  const match = prompt.match(/(\d+)\s*-?\s*days?/i);
  return match ? `${match[1]} days` : '';
}

function origin(prompt: string): string {
  const match = prompt.match(/\bfrom\s+([A-Za-z]{3,})(?:\s+(?:including|under|with|for|and|,)|$)/i);
  const raw = match?.[1]?.trim() ?? '';
  return raw ? raw.charAt(0).toUpperCase() + raw.slice(1) : '';
}

function friendlyWhen(iso?: string): string {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  const hours = (Date.now() - date.getTime()) / 36e5;
  if (hours < 1) return 'Just now';
  if (hours < 18) return 'Today';
  if (hours < 42) return 'Yesterday';
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function statusCopy(status: string): { label: string; cta: string } {
  switch (status) {
    case 'awaiting_approval':
      return { label: 'Ready to review', cta: 'Open this draft' };
    case 'completed':
      return { label: 'Trip ready', cta: 'Open this trip' };
    case 'blocked':
      return { label: 'Needs a new direction', cta: 'See what happened' };
    case 'failed':
      return { label: 'Didn’t finish', cta: 'Try again' };
    default:
      return { label: 'Still sketching', cta: 'Continue' };
  }
}

export function tripStory(record: TravelRequestRecord): TripStory {
  const prompt = record.prompt || '';
  const { place, title, country } = matchPlace(prompt);
  const days = duration(prompt);
  const from = origin(prompt);
  const vibe = title === place.name ? place.vibe : '';
  const bits = [days, from ? `from ${from}` : '', vibe].filter(Boolean);
  const { label, cta } = statusCopy(record.status);
  const href =
    record.status === 'awaiting_approval'
      ? ['/approvals', record.thread_id]
      : ['/requests', record.thread_id];

  return {
    title,
    country,
    vibe: place.vibe,
    image: place.image,
    line: bits.join(' · '),
    when: friendlyWhen(record.updated_at || record.created_at),
    status: label,
    cta,
    href,
  };
}
