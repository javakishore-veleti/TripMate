import { photoForPlace } from './trip-story';

export type Horizon = 'week' | 'month' | 'quarter';
export type MomentKind = 'festival' | 'culture' | 'season';

export interface SeasonMoment {
  id: string;
  name: string;
  country: string;
  placeName: string;
  kind: MomentKind;
  months: number[];
  week?: boolean;
  blurb: string;
  image?: string;
}

export interface MomentCard extends SeasonMoment {
  image: string;
  why: string;
  kindLabel: string;
}

export const PACK_COUNTRIES: Record<string, string[]> = {
  'beach-escape': ['Greece', 'Maldives', 'Thailand', 'Indonesia', 'USA'],
  'family-weekends': ['USA', 'Japan', 'UK', 'Singapore', 'France'],
  'couple-getaway': ['Italy', 'France', 'Greece', 'Japan'],
  'city-break': ['UK', 'France', 'USA', 'Japan', 'Spain'],
  'nature-outdoors': ['Canada', 'New Zealand', 'Nepal', 'Tanzania', 'USA'],
  'budget-travel': ['Thailand', 'Vietnam', 'Portugal', 'India', 'Spain'],
  'solo-explorer': ['Japan', 'Portugal', 'Vietnam', 'Spain'],
  'business-trip': ['Singapore', 'UK', 'USA', 'Japan'],
};

const KIND_LABEL: Record<MomentKind, string> = {
  festival: 'Festival',
  culture: 'Culture',
  season: 'In season',
};

const MOMENTS: SeasonMoment[] = [
  { id: 'jp-hatsumode', name: 'Hatsumode', country: 'Japan', placeName: 'Kyoto', kind: 'culture', months: [1], blurb: 'First shrine visit of the year — lanterns, wishes, warm amazake.' },
  { id: 'jp-snow', name: 'Sapporo Snow Festival', country: 'Japan', placeName: 'Tokyo', kind: 'festival', months: [2], blurb: 'Ice sculptures and night lights. Pair with an onsen stop.' },
  { id: 'jp-sakura', name: 'Cherry blossom weeks', country: 'Japan', placeName: 'Kyoto', kind: 'season', months: [3, 4], week: true, blurb: 'Hanami picnics under pink canopies. Book stays early.' },
  { id: 'jp-golden', name: 'Golden Week', country: 'Japan', placeName: 'Tokyo', kind: 'culture', months: [4, 5], blurb: 'A national travel rush. Trains and temples are lively.' },
  { id: 'jp-gion', name: 'Gion Matsuri', country: 'Japan', placeName: 'Kyoto', kind: 'festival', months: [7], blurb: 'Floats, yukata, and Kyoto’s summer night streets.' },
  { id: 'jp-obon', name: 'Obon', country: 'Japan', placeName: 'Kyoto', kind: 'culture', months: [8], blurb: 'Lanterns for ancestors. Cities empty a little; towns glow.' },
  { id: 'jp-autumn', name: 'Momiji season', country: 'Japan', placeName: 'Kyoto', kind: 'season', months: [9, 10, 11], week: true, blurb: 'Maple reds start in the mountains, then drop into the cities.' },
  { id: 'in-holi', name: 'Holi', country: 'India', placeName: 'Jaipur', kind: 'festival', months: [3], blurb: 'Color, music, and street sweets. Pack clothes you can ruin happily.' },
  { id: 'in-monsoon', name: 'Monsoon green', country: 'India', placeName: 'Kerala', kind: 'season', months: [6, 7, 8, 9], week: true, blurb: 'Backwaters and Western Ghats turn luminous. Slow days, heavy skies.' },
  { id: 'in-onam', name: 'Onam', country: 'India', placeName: 'Kerala', kind: 'festival', months: [8, 9], week: true, blurb: 'Boat races, flower carpets, and a feast that takes the whole table.' },
  { id: 'in-ganesh', name: 'Ganesh Chaturthi', country: 'India', placeName: 'Mumbai', kind: 'festival', months: [8, 9], week: true, blurb: 'Processions to the sea. Mumbai and Pune are electric.' },
  { id: 'in-durga', name: 'Durga Puja', country: 'India', placeName: 'Varanasi', kind: 'festival', months: [9, 10], blurb: 'Pandal art, drums, and evening lights across the east.' },
  { id: 'in-diwali', name: 'Diwali', country: 'India', placeName: 'Jaipur', kind: 'festival', months: [10, 11], blurb: 'Lamps on every ledge. Cities stay up late and smell of sweets.' },
  { id: 'in-pushkar', name: 'Pushkar Camel Fair', country: 'India', placeName: 'Jaipur', kind: 'culture', months: [11], blurb: 'Desert market, folk nights, and a holy lake town at full tilt.' },
  { id: 'it-carnival', name: 'Carnevale', country: 'Italy', placeName: 'Venice', kind: 'festival', months: [2], blurb: 'Masks on the canals. Book if you like theater in the streets.' },
  { id: 'it-pasqua', name: 'Easter in Rome', country: 'Italy', placeName: 'Rome', kind: 'culture', months: [3, 4], blurb: 'Processions and packed piazzas. Quiet Tuesday after is a gift.' },
  { id: 'it-estate', name: 'Long Italian evenings', country: 'Italy', placeName: 'Amalfi', kind: 'season', months: [6, 7, 8], blurb: 'Coast swims and late dinners. Heat is part of the deal.' },
  { id: 'it-vendemmia', name: 'Vendemmia', country: 'Italy', placeName: 'Florence', kind: 'season', months: [9, 10], week: true, blurb: 'Grape harvest in the hills. Villages smell like crushed fruit.' },
  { id: 'fr-fete', name: 'Fête de la Musique', country: 'France', placeName: 'Paris', kind: 'festival', months: [6], blurb: 'Free concerts on every corner. Stay out later than planned.' },
  { id: 'fr-harvest', name: 'Wine harvest', country: 'France', placeName: 'Lyon', kind: 'season', months: [9, 10], week: true, blurb: 'Vines turn gold. Easy train hops from Lyon or Paris.' },
  { id: 'fr-lumières', name: 'Fête des Lumières', country: 'France', placeName: 'Lyon', kind: 'festival', months: [12], blurb: 'The city becomes a lantern. Book rooms early.' },
  { id: 'es-merce', name: 'La Mercè', country: 'Spain', placeName: 'Barcelona', kind: 'festival', months: [9], week: true, blurb: 'Human towers, fireworks, and Barcelona’s biggest street party.' },
  { id: 'es-fallas', name: 'Las Fallas', country: 'Spain', placeName: 'Barcelona', kind: 'festival', months: [3], blurb: 'Sculptures, fire, and nights that do not pretend to end.' },
  { id: 'gr-summer', name: 'Island high season', country: 'Greece', placeName: 'Santorini', kind: 'season', months: [6, 7, 8, 9], week: true, blurb: 'Still swimming weather. Ferries run often; sunsets are crowded on purpose.' },
  { id: 'gr-easter', name: 'Greek Easter', country: 'Greece', placeName: 'Athens', kind: 'culture', months: [4, 5], blurb: 'Midnight fire, lamb, and villages that feel like a family table.' },
  { id: 'th-songkran', name: 'Songkran', country: 'Thailand', placeName: 'Bangkok', kind: 'festival', months: [4], blurb: 'Water fights in the streets. Smile and expect to get soaked.' },
  { id: 'th-loy', name: 'Loy Krathong', country: 'Thailand', placeName: 'Chiang Mai', kind: 'festival', months: [11], blurb: 'Lanterns on the river. Chiang Mai is the postcard version.' },
  { id: 'th-cool', name: 'Cool-season north', country: 'Thailand', placeName: 'Chiang Mai', kind: 'season', months: [11, 12, 1, 2], blurb: 'Crisp mornings, temple walks, and night markets without the heaviest heat.' },
  { id: 'id-dry', name: 'Bali dry season', country: 'Indonesia', placeName: 'Ubud', kind: 'season', months: [5, 6, 7, 8, 9], week: true, blurb: 'Rice terraces in clear light. Still green, fewer afternoon floods.' },
  { id: 'us-labor', name: 'Late-summer US', country: 'USA', placeName: 'San Diego', kind: 'season', months: [8, 9], week: true, blurb: 'Beaches and parks still in summer mode. School calendars start to shift.' },
  { id: 'us-fall', name: 'New England color', country: 'USA', placeName: 'New York', kind: 'season', months: [10], blurb: 'Leaves and apple stands. Easy add-on from New York.' },
  { id: 'us-thanksgiving', name: 'Thanksgiving week', country: 'USA', placeName: 'New York', kind: 'culture', months: [11], blurb: 'Parades and family tables. Flights get tight — plan the buffer.' },
  { id: 'mx-independencia', name: 'Independence days', country: 'Mexico', placeName: 'Mexico City', kind: 'festival', months: [9], week: true, blurb: 'El Grito, flags, and plazas that stay loud past midnight.' },
  { id: 'mx-muertos', name: 'Día de Muertos', country: 'Mexico', placeName: 'Mexico City', kind: 'culture', months: [10, 11], blurb: 'Altars, marigolds, and a night that is tender more than scary.' },
  { id: 'uk-may', name: 'Bank-holiday Britain', country: 'UK', placeName: 'London', kind: 'season', months: [5], blurb: 'Long weekends, parks, and trains to the coast.' },
  { id: 'uk-harvest', name: 'Harvest weekends', country: 'UK', placeName: 'Edinburgh', kind: 'season', months: [9, 10], week: true, blurb: 'Markets, wool, and walks that want a jacket by late afternoon.' },
  { id: 'uk-hogmanay', name: 'Hogmanay', country: 'UK', placeName: 'Edinburgh', kind: 'festival', months: [12, 1], blurb: 'Edinburgh’s new year. Book if you like a crowd that sings.' },
  { id: 'tr-balloon', name: 'Cappadocia balloon mornings', country: 'Türkiye', placeName: 'Cappadocia', kind: 'season', months: [4, 5, 9, 10], week: true, blurb: 'Clear, cool dawn flights. Shoulder season is the sweet one.' },
  { id: 'ma-rose', name: 'Rose season', country: 'Morocco', placeName: 'Marrakech', kind: 'season', months: [4, 5], blurb: 'Valleys south of Marrakech smell like the souk before the heat lands.' },
  { id: 'eg-winter', name: 'Nile high season', country: 'Egypt', placeName: 'Cairo', kind: 'season', months: [11, 12, 1, 2, 3], blurb: 'Mild days for temples. Summer is a different kind of brave.' },
  { id: 'ke-wildebeest', name: 'Migration window', country: 'Kenya', placeName: 'Nairobi', kind: 'season', months: [7, 8, 9, 10], week: true, blurb: 'River crossings and long grass. Pair Nairobi with a short bush stay.' },
  { id: 'tz-wildebeest', name: 'Serengeti movement', country: 'Tanzania', placeName: 'Serengeti', kind: 'season', months: [6, 7, 8, 9], week: true, blurb: 'The herds keep walking. Zanzibar is the salt-water epilogue.' },
  { id: 'np-autumn', name: 'Himalaya autumn', country: 'Nepal', placeName: 'Pokhara', kind: 'season', months: [10, 11], blurb: 'Clear peaks after the monsoon. Trails and lake mornings.' },
  { id: 'np-dashain', name: 'Dashain', country: 'Nepal', placeName: 'Kathmandu', kind: 'festival', months: [10], blurb: 'Family fortnight. Kites over the valley, shops that keep their own time.' },
  { id: 'pt-sardines', name: 'Santos Populares', country: 'Portugal', placeName: 'Lisbon', kind: 'festival', months: [6], blurb: 'Sardines on the grill, paper decorations, and hills that bounce.' },
  { id: 'br-carnival', name: 'Carnaval', country: 'Brazil', placeName: 'Rio de Janeiro', kind: 'festival', months: [2], blurb: 'Samba that starts before you are ready. Sleep is a rumor.' },
  { id: 'ca-fall', name: 'Maple weeks', country: 'Canada', placeName: 'Banff', kind: 'season', months: [9, 10], week: true, blurb: 'Gold aspen and cold lakes. Banff starts to feel like a wool town.' },
  { id: 'nz-summer', name: 'Southern summer', country: 'New Zealand', placeName: 'Queenstown', kind: 'season', months: [12, 1, 2], blurb: 'Long light, trailheads, and a jump if you want one.' },
  { id: 'au-summer', name: 'Australian summer', country: 'Australia', placeName: 'Gold Coast', kind: 'season', months: [12, 1, 2], blurb: 'Surf and late evenings. Boxing Day to Australia Day is peak buzz.' },
  { id: 'vn-tet', name: 'Tết', country: 'Vietnam', placeName: 'Hoi An', kind: 'festival', months: [1, 2], blurb: 'New year flowers and quiet first days. Book around the shutdown.' },
  { id: 'vn-lantern', name: 'Hoi An full-moon nights', country: 'Vietnam', placeName: 'Hoi An', kind: 'culture', months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], week: true, blurb: 'Lantern river once a month. The town already looks like a wish.' },
  { id: 'de-oktoberfest', name: 'Oktoberfest', country: 'Germany', placeName: 'Munich', kind: 'festival', months: [9, 10], week: true, blurb: 'Tents, brass, and a city that runs on reservations. Pair with a lake day.', image: 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?auto=format&fit=crop&w=1200&q=70' },
  { id: 'kr-chuseok', name: 'Chuseok', country: 'South Korea', placeName: 'Seoul', kind: 'culture', months: [9], week: true, blurb: 'Harvest homecoming. Seoul empties a little; the old palaces feel closer.' },
  { id: 'cn-moon', name: 'Mid-Autumn Festival', country: 'China', placeName: 'Hong Kong', kind: 'festival', months: [9], week: true, blurb: 'Mooncakes and lanterns. Hong Kong harbor does the postcard version.' },
];

const WANDER_COUNTRIES = ['Japan', 'India', 'Italy', 'Mexico', 'USA', 'Greece'];

export function horizonLabel(horizon: Horizon, date = new Date()): string {
  if (horizon === 'week') {
    return `This week · ${date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}`;
  }
  if (horizon === 'month') {
    return date.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  }
  const quarter = Math.floor(date.getMonth() / 3) + 1;
  return `Q${quarter} ${date.getFullYear()}`;
}

export function quarterMonths(date = new Date()): number[] {
  const start = Math.floor(date.getMonth() / 3) * 3 + 1;
  return [start, start + 1, start + 2];
}

function inHorizon(moment: SeasonMoment, horizon: Horizon, date: Date): boolean {
  const month = date.getMonth() + 1;
  if (horizon === 'week') {
    return moment.months.includes(month) && Boolean(moment.week);
  }
  if (horizon === 'month') {
    return moment.months.includes(month);
  }
  return moment.months.some((item) => quarterMonths(date).includes(item));
}

export function interestsFromPacks(ids: string[]): string[] {
  const countries = new Set<string>();
  for (const id of ids) {
    for (const country of PACK_COUNTRIES[id] ?? []) {
      countries.add(country);
    }
  }
  return [...countries];
}

export function momentsFor(
  horizon: Horizon,
  interested: string[],
  reasons: Record<string, string>,
  date = new Date(),
): MomentCard[] {
  const focus = interested.length ? interested : WANDER_COUNTRIES;
  const focusSet = new Set(focus.map((item) => item.toLowerCase()));

  const scored = MOMENTS.filter((moment) => inHorizon(moment, horizon, date)).map((moment) => {
    const hit = focusSet.has(moment.country.toLowerCase());
    return {
      ...moment,
      image: moment.image || photoForPlace(moment.placeName, moment.country),
      why: hit ? reasons[moment.country] || `On your map: ${moment.country}` : 'A moment worth knowing',
      kindLabel: KIND_LABEL[moment.kind],
      hit,
    };
  });

  scored.sort((a, b) => Number(b.hit) - Number(a.hit));
  const preferred = scored.filter((item) => item.hit);
  const pool = preferred.length >= 3 ? preferred : scored;
  return pool.slice(0, 6);
}
