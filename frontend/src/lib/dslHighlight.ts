import Prism from "prismjs";
import "prismjs/components/prism-clike";
import "prismjs/components/prism-javascript";

Prism.languages.dsl = {
  'comment': /\/\/.*$/m,
  'keyword': /\b(Room|Door|Table|Chair|Window|Bed|Sofa|Desk|Wardrobe|Lamp|Shelf)\b/,
  'string': /"(?:\\.|[^\\"])*"/,
  'number': /\b\d+(\.\d+)?\b/,
  'punctuation': /[{}[\];(),.:]/,
};

export function highlight(code: string) {
  return Prism.highlight(code, Prism.languages.dsl, "dsl");
}