export function highlightText(text: string, keyword: string) {
  if (!keyword) return text;

  const regex = new RegExp(`(${keyword})`, "gi");

  return text.replace(regex, `<mark class="bg-yellow-200">$1</mark>`);
}
