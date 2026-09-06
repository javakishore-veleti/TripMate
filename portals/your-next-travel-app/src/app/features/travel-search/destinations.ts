export interface Destination {
  name: string;
  country: string;
  vibe: string;
  image: string;
}

export interface DestinationGroup {
  id: string;
  title: string;
  subtitle: string;
  emoji: string;
  places: Destination[];
}

function photo(id: string): string {
  return `https://images.unsplash.com/${id}?auto=format&fit=crop&w=900&q=70`;
}

export const DESTINATION_GROUPS: DestinationGroup[] = [
  {
    id: 'family',
    title: 'Family favorites',
    subtitle: 'Easy days, big smiles, something for every age',
    emoji: '👨‍👩‍👧‍👦',
    places: [
      { name: 'Orlando', country: 'USA', vibe: 'Parks & pancakes', image: photo('photo-1566073771259-6a8506099945') },
      { name: 'San Diego', country: 'USA', vibe: 'Zoo, beach, tacos', image: photo('photo-1507525428034-b723cf961d3e') },
      { name: 'Singapore', country: 'Singapore', vibe: 'Gardens & lights', image: photo('photo-1525625293386-3f8f99389edd') },
      { name: 'Tokyo', country: 'Japan', vibe: 'TeamLab & ramen', image: photo('photo-1540959733332-eab4deabeeaf') },
      { name: 'London', country: 'UK', vibe: 'Museums & buses', image: photo('photo-1513635269975-59663e0ac1ad') },
      { name: 'Paris', country: 'France', vibe: 'Pastries & parks', image: photo('photo-1502602898657-3e91760cbb34') },
      { name: 'Barcelona', country: 'Spain', vibe: 'Gaudi & gelato', image: photo('photo-1539037116277-4db20889f2d4') },
      { name: 'Rome', country: 'Italy', vibe: 'Gelato between ruins', image: photo('photo-1552832230-c0197dd311b5') },
      { name: 'Dubai', country: 'UAE', vibe: 'Fountain nights', image: photo('photo-1512453979798-5ea266f8880c') },
      { name: 'Gold Coast', country: 'Australia', vibe: 'Surf & theme parks', image: photo('photo-1506973035872-a4ec16b8e8d9') },
    ],
  },
  {
    id: 'asia',
    title: 'Asia calling',
    subtitle: 'Temples, night markets, bullet trains',
    emoji: '🏮',
    places: [
      { name: 'Kyoto', country: 'Japan', vibe: 'Lanterns & gardens', image: photo('photo-1524413840807-0c3cb6fa808d') },
      { name: 'Osaka', country: 'Japan', vibe: 'Street food heaven', image: photo('photo-1554797589-7241bb691973') },
      { name: 'Seoul', country: 'South Korea', vibe: 'Palaces & K-food', image: photo('photo-1540959733332-eab4deabeeaf') },
      { name: 'Bangkok', country: 'Thailand', vibe: 'River & markets', image: photo('photo-1508009603885-50cf7c579365') },
      { name: 'Chiang Mai', country: 'Thailand', vibe: 'Lantern nights', image: photo('photo-1528127269322-539801943592') },
      { name: 'Hoi An', country: 'Vietnam', vibe: 'Yellow lantern town', image: photo('photo-1528127269322-539801943592') },
      { name: 'Hanoi', country: 'Vietnam', vibe: 'Coffee & lakes', image: photo('photo-1583417319070-4a69db38a482') },
      { name: 'Bali', country: 'Indonesia', vibe: 'Rice terraces', image: photo('photo-1518548419970-58e3b4079ab2') },
      { name: 'Ubud', country: 'Indonesia', vibe: 'Jungle calm', image: photo('photo-1518548419970-58e3b4079ab2') },
      { name: 'Hong Kong', country: 'China', vibe: 'Skyline ferry', image: photo('photo-1506973035872-a4ec16b8e8d9') },
    ],
  },
  {
    id: 'india',
    title: 'India & the Himalayas',
    subtitle: 'Color, spice, snow, and stories',
    emoji: '🕌',
    places: [
      { name: 'Jaipur', country: 'India', vibe: 'Pink city glow', image: photo('photo-1477587458883-47145ed94245') },
      { name: 'Udaipur', country: 'India', vibe: 'Lake palaces', image: photo('photo-1564507592333-c60657eea523') },
      { name: 'Agra', country: 'India', vibe: 'Sunrise marble', image: photo('photo-1564507592333-c60657eea523') },
      { name: 'Varanasi', country: 'India', vibe: 'River lamps', image: photo('photo-1561361513-2d000a50f0dc') },
      { name: 'Kerala', country: 'India', vibe: 'Backwater boats', image: photo('photo-1602216056096-3b40cc0c9944') },
      { name: 'Goa', country: 'India', vibe: 'Beaches & spice', image: photo('photo-1512343879784-a960bf40e7f2') },
      { name: 'Mumbai', country: 'India', vibe: 'Sea and cinema', image: photo('photo-1512453979798-5ea266f8880c') },
      { name: 'Leh', country: 'India', vibe: 'High desert sky', image: photo('photo-1506905925346-21bda4d32df4') },
      { name: 'Kathmandu', country: 'Nepal', vibe: 'Temple squares', image: photo('photo-1544735716-392fe2489ffa') },
      { name: 'Pokhara', country: 'Nepal', vibe: 'Lake & peaks', image: photo('photo-1605640840605-14ac1855827b') },
    ],
  },
  {
    id: 'europe',
    title: 'Europe weekends',
    subtitle: 'Trains, plazas, and dessert first',
    emoji: '🚂',
    places: [
      { name: 'Amsterdam', country: 'Netherlands', vibe: 'Canals at dusk', image: photo('photo-1555881400-74d7acaacd8b') },
      { name: 'Prague', country: 'Czechia', vibe: 'Fairytale bridges', image: photo('photo-1541849546-216549ae216d') },
      { name: 'Vienna', country: 'Austria', vibe: 'Cakes & concerts', image: photo('photo-1516550893923-42d28e5677af') },
      { name: 'Budapest', country: 'Hungary', vibe: 'Baths & lights', image: photo('photo-1551867633-194f125bddfa') },
      { name: 'Lisbon', country: 'Portugal', vibe: 'Trams & tiles', image: photo('photo-1555881400-74d7acaacd8b') },
      { name: 'Porto', country: 'Portugal', vibe: 'River wine town', image: photo('photo-1555881400-74d7acaacd8b') },
      { name: 'Florence', country: 'Italy', vibe: 'Art & gelato', image: photo('photo-1552832230-c0197dd311b5') },
      { name: 'Venice', country: 'Italy', vibe: 'Quiet canals', image: photo('photo-1514890547357-a9ee288728e0') },
      { name: 'Athens', country: 'Greece', vibe: 'Ruins in sunlight', image: photo('photo-1555993539-1732b0258235') },
      { name: 'Edinburgh', country: 'UK', vibe: 'Castle walks', image: photo('photo-1513635269975-59663e0ac1ad') },
    ],
  },
  {
    id: 'islands',
    title: 'Islands & blue water',
    subtitle: 'For kids who love sand and grown-ups who love stillness',
    emoji: '🏝️',
    places: [
      { name: 'Santorini', country: 'Greece', vibe: 'White & blue', image: photo('photo-1613395877344-13d4a8e0d49e') },
      { name: 'Mykonos', country: 'Greece', vibe: 'Windmills', image: photo('photo-1533104816931-20fa691ff6ca') },
      { name: 'Maldives', country: 'Maldives', vibe: 'Overwater quiet', image: photo('photo-1559827260-dc66d52bef19') },
      { name: 'Maui', country: 'USA', vibe: 'Road to Hana', image: photo('photo-1542259009477-d625272157b7') },
      { name: 'Maui Coast', country: 'USA', vibe: 'Sunrise water', image: photo('photo-1469796466635-455ede028aca') },
      { name: 'Phuket', country: 'Thailand', vibe: 'Long-tail boats', image: photo('photo-1589394815804-964ed0be2eb5') },
      { name: 'Phu Quoc', country: 'Vietnam', vibe: 'Palm beaches', image: photo('photo-1559827260-dc66d52bef19') },
      { name: 'Zanzibar', country: 'Tanzania', vibe: 'Spice island', image: photo('photo-1544551763-46a013bb70d5') },
      { name: 'Seychelles', country: 'Seychelles', vibe: 'Granite coves', image: photo('photo-1507525428034-b723cf961d3e') },
      { name: 'Fiji', country: 'Fiji', vibe: 'Village smiles', image: photo('photo-1439066615861-d1af74d74000') },
    ],
  },
  {
    id: 'americas',
    title: 'The Americas',
    subtitle: 'Road trips, cities, and national-park wow',
    emoji: '🗽',
    places: [
      { name: 'New York', country: 'USA', vibe: 'Lights that never quit', image: photo('photo-1480714378408-67cf0d13bc1b') },
      { name: 'San Francisco', country: 'USA', vibe: 'Fog & hills', image: photo('photo-1501594907352-04cda38ebc29') },
      { name: 'Banff', country: 'Canada', vibe: 'Lake mirrors', image: photo('photo-1441974231531-c6227db76b6e') },
      { name: 'Vancouver', country: 'Canada', vibe: 'Sea and cedar', image: photo('photo-1559511260-66a654ae982a') },
      { name: 'Mexico City', country: 'Mexico', vibe: 'Color & cuisine', image: photo('photo-1483729558449-99ef09a8c325') },
      { name: 'Cancun', country: 'Mexico', vibe: 'Turquoise days', image: photo('photo-1510097467424-192d713fd8b2') },
      { name: 'Cusco', country: 'Peru', vibe: 'Inca streets', image: photo('photo-1526392060635-9d6019884377') },
      { name: 'Rio de Janeiro', country: 'Brazil', vibe: 'Hills & samba', image: photo('photo-1483729558449-99ef09a8c325') },
      { name: 'Buenos Aires', country: 'Argentina', vibe: 'Steaks & tango', image: photo('photo-1589909202802-8f4aadce1849') },
      { name: 'Patagonia', country: 'Chile', vibe: 'Wind and granite', image: photo('photo-1464822759023-fed622ff2c3b') },
    ],
  },
  {
    id: 'africa',
    title: 'Africa & the Middle East',
    subtitle: 'Safari mornings and old-city evenings',
    emoji: '🦁',
    places: [
      { name: 'Cape Town', country: 'South Africa', vibe: 'Mountain & sea', image: photo('photo-1580060839134-75a5edca2e99') },
      { name: 'Marrakech', country: 'Morocco', vibe: 'Souks & courtyards', image: photo('photo-1523805009345-7448845a9e53') },
      { name: 'Cairo', country: 'Egypt', vibe: 'Pyramids at dusk', image: photo('photo-1564507592333-c60657eea523') },
      { name: 'Petra', country: 'Jordan', vibe: 'Rose-red canyon', image: photo('photo-1464822759023-fed622ff2c3b') },
      { name: 'Istanbul', country: 'Türkiye', vibe: 'Two continents', image: photo('photo-1524231757912-21f4fe3a7200') },
      { name: 'Cappadocia', country: 'Türkiye', vibe: 'Balloons at dawn', image: photo('photo-1519681393784-d120267933ba') },
      { name: 'Jerusalem', country: 'Israel', vibe: 'Old city stone', image: photo('photo-1524231757912-21f4fe3a7200') },
      { name: 'Nairobi', country: 'Kenya', vibe: 'City + safari', image: photo('photo-1516426122078-c23e76319801') },
      { name: 'Serengeti', country: 'Tanzania', vibe: 'Endless grass', image: photo('photo-1547471080-7cc2caa01a7e') },
      { name: 'Zanzibar Stone Town', country: 'Tanzania', vibe: 'Doors & spice', image: photo('photo-1523805009345-7448845a9e53') },
    ],
  },
  {
    id: 'adventure',
    title: 'Adventure & mountains',
    subtitle: 'For teens with energy and grandparents with binoculars',
    emoji: '⛰️',
    places: [
      { name: 'Interlaken', country: 'Switzerland', vibe: 'Lakes between peaks', image: photo('photo-1531366936337-7c912a4589a7') },
      { name: 'Zermatt', country: 'Switzerland', vibe: 'Matterhorn views', image: photo('photo-1531366936337-7c912a4589a7') },
      { name: 'Queenstown', country: 'New Zealand', vibe: 'Jump and then tea', image: photo('photo-1469854523086-cc02fe5d8800') },
      { name: 'Reykjavik', country: 'Iceland', vibe: 'Steam & northern lights', image: photo('photo-1500043357865-c6b8827edf10') },
      { name: 'Tromsø', country: 'Norway', vibe: 'Arctic glow', image: photo('photo-1483347756197-71ef80e95f73') },
      { name: 'Banff Trail', country: 'Canada', vibe: 'Pine and turquoise', image: photo('photo-1501785888041-af3ef285b470') },
      { name: 'Moab', country: 'USA', vibe: 'Red rock rides', image: photo('photo-1464822759023-fed622ff2c3b') },
      { name: 'Machu Picchu', country: 'Peru', vibe: 'Cloud ruins', image: photo('photo-1587595431973-160d0d94add1') },
      { name: 'Everest View', country: 'Nepal', vibe: 'Himalaya morning', image: photo('photo-1506905925346-21bda4d32df4') },
      { name: 'Alps Train', country: 'Switzerland', vibe: 'Window-seat wow', image: photo('photo-1464822759023-fed622ff2c3b') },
    ],
  },
  {
    id: 'food',
    title: 'Food-first trips',
    subtitle: 'Kids want snacks. Everyone else wants a second dinner.',
    emoji: '🍜',
    places: [
      { name: 'Osaka Night', country: 'Japan', vibe: 'Takoyaki alleys', image: photo('photo-1554797589-7241bb691973') },
      { name: 'Bangkok Eats', country: 'Thailand', vibe: 'Boat noodles', image: photo('photo-1504674900247-0877df9cc836') },
      { name: 'Penang', country: 'Malaysia', vibe: 'Hawker heaven', image: photo('photo-1559339352-11d035aa65de') },
      { name: 'Taipei', country: 'Taiwan', vibe: 'Night market bites', image: photo('photo-1470004914212-05527e49370b') },
      { name: 'Lyon', country: 'France', vibe: 'Bouchon dinners', image: photo('photo-1414235077428-338989a2e8c0') },
      { name: 'Bologna', country: 'Italy', vibe: 'Pasta class', image: photo('photo-1621996346565-e3dbc646d9a9') },
      { name: 'Istanbul Eats', country: 'Türkiye', vibe: 'Kebab & baklava', image: photo('photo-1524231757912-21f4fe3a7200') },
      { name: 'Mexico City Eats', country: 'Mexico', vibe: 'Tacos al pastor', image: photo('photo-1565299624946-b28f40a0ae38') },
      { name: 'New Orleans', country: 'USA', vibe: 'Jazz and beignets', image: photo('photo-1569949381669-ecf31ae8e613') },
      { name: 'Melbourne', country: 'Australia', vibe: 'Coffee lanes', image: photo('photo-1514395462725-fb4566210144') },
    ],
  },
  {
    id: 'calm',
    title: 'Slow & beautiful',
    subtitle: 'Soft light, fewer plans, more sitting still',
    emoji: '🌅',
    places: [
      { name: 'Kyoto Gardens', country: 'Japan', vibe: 'Moss and water', image: photo('photo-1524413840807-0c3cb6fa808d') },
      { name: 'Lake Como', country: 'Italy', vibe: 'Ferry afternoons', image: photo('photo-1469474968028-56623f02e42e') },
      { name: 'Amalfi', country: 'Italy', vibe: 'Lemon cliffs', image: photo('photo-1533106497176-45ae19e68ba2') },
      { name: 'Hallstatt', country: 'Austria', vibe: 'Alpine village', image: photo('photo-1519681393784-d120267933ba') },
      { name: 'Queenstown Lake', country: 'New Zealand', vibe: 'Still water', image: photo('photo-1469474968028-56623f02e42e') },
      { name: 'Ubud Rice', country: 'Indonesia', vibe: 'Morning mist', image: photo('photo-1518548419970-58e3b4079ab2') },
      { name: 'Santorini Sunset', country: 'Greece', vibe: 'Orange hour', image: photo('photo-1613395877344-13d4a8e0d49e') },
      { name: 'Kyoto Night', country: 'Japan', vibe: 'Quiet alleys', image: photo('photo-1524413840807-0c3cb6fa808d') },
      { name: 'Banff Night', country: 'Canada', vibe: 'Star lakes', image: photo('photo-1501785888041-af3ef285b470') },
      { name: 'Maldives Dawn', country: 'Maldives', vibe: 'Empty horizon', image: photo('photo-1559827260-dc66d52bef19') },
    ],
  },
];
