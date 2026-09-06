export type ModelHintPage = 'dashboard' | 'journal' | 'plan' | 'preferences' | 'account';

export interface ModelHintCopy {
  before: string;
  link: string;
  after: string;
}

const HINTS: Record<ModelHintPage, ModelHintCopy> = {
  dashboard: {
    before: 'These nearby briefs can go deeper from ',
    link: 'Account',
    after: '.',
  },
  journal: {
    before: 'This month can go deeper from ',
    link: 'Account',
    after: '.',
  },
  plan: {
    before: 'The trip sketch is still folding its map. ',
    link: 'Account',
    after: '',
  },
  preferences: {
    before: 'This packs note is still finding its voice. ',
    link: 'Account',
    after: '',
  },
  account: {
    before: 'The other menus are still warming up. ',
    link: 'Models',
    after: '',
  },
};

export function modelHintFor(page: ModelHintPage): ModelHintCopy {
  return HINTS[page];
}

export function isModelConfigMessage(message?: string | null): boolean {
  const text = message || '';
  return (
    text.includes('No local Ollama model') ||
    text.includes('No Ollama model selected') ||
    text.includes('Ollama is not reachable') ||
    text.includes('Pick a model on your account first')
  );
}

export function needsModelHint(payload?: { needs_model?: boolean; message?: string } | null): boolean {
  return Boolean(payload?.needs_model) || isModelConfigMessage(payload?.message);
}
