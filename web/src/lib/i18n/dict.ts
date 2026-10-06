import dict from "./locale-zh.json";
import { useLocale } from "./store";

export const EN_TO_ZH: Record<string, string> = {};

for (const [zh, en] of Object.entries(dict as Record<string, string>)) {
  EN_TO_ZH[en] = zh;
}

export function translateTextNode(s: string): string {
  if (useLocale.getState().locale !== "zh") {
    return s;
  }
  const exact = EN_TO_ZH[s];
  if (exact !== undefined) {
    return exact;
  }
  const trimmed = s.trim();
  if (trimmed && EN_TO_ZH[trimmed] !== undefined) {
    const start = s.indexOf(trimmed);
    return `${s.slice(0, start)}${EN_TO_ZH[trimmed]}${s.slice(start + trimmed.length)}`;
  }
  return s;
}
