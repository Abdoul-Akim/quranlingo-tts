// Run from the TTS folder:  node --test tests/web/*.test.mjs
import assert from "node:assert/strict";
import { test } from "node:test";

import { buildPages, isRtl, newSession, renderMarkdown, voteBody } from "../../aws_site/web/logic.js";

const item = (name, clips, extra = {}) => ({ item: name, label: name, clips, ...extra });
const rounds = {
  base_fr: { question: "Which?", items: [item("ali", ["a1", "a2", "a3"]), item("omar", ["o1", "o2"])] },
};
const config = {
  pages: [
    { path: "fr", name: "Français", language: "fr", intro: "# Bonjour",
      rounds: [{ round: "base_fr", heading: "Partie 1", same_label: "Égal", question: "Quelle voix ?" },
               { round: "lines_fr", heading: "Partie 2", same_label: "Égal" }] },
    { path: "de", name: "Deutsch", language: "de", intro: "",
      rounds: [{ round: "base_de", heading: "Teil 1", same_label: "Gleich" }] },
  ],
};

test("pages only show rounds that exist, and empty pages are left out", () => {
  const pages = buildPages(config, rounds);
  assert.deepEqual(pages.map((p) => p.path), ["fr"]);
  assert.deepEqual(pages[0].questions.map((q) => q.item), ["ali", "omar"]);
  assert.equal(pages[0].questions[0].question, "Quelle voix ?"); // the page's own language
});

test("up to five takes per question, more is refused", () => {
  const five = { r: { question: "Q", items: [item("ali", ["a", "b", "c", "d", "e"])] } };
  const six = { r: { question: "Q", items: [item("ali", ["a", "b", "c", "d", "e", "f"])] } };
  const cfg = { pages: [{ path: "", name: "E", language: "en", intro: "", rounds: [{ round: "r", heading: "H", same_label: "S" }] }] };
  assert.equal(buildPages(cfg, five)[0].questions[0].clips.length, 5);
  assert.throws(() => buildPages(cfg, six));
});

test("each visitor hears every clip once, in a shuffled order", () => {
  const [page] = buildPages(config, rounds);
  let n = 0;
  const random = () => ((n = (n * 7 + 3) % 10) / 10);
  const session = newSession(page, random, () => "f".repeat(32));
  assert.equal(session.tester_id, "f".repeat(32));
  assert.deepEqual([...session.order[0]].sort(), ["a1", "a2", "a3"]);
  assert.deepEqual([...session.order[1]].sort(), ["o1", "o2"]);
});

test("the vote body names the clips in the order they were shown", () => {
  const [page] = buildPages(config, rounds);
  const session = { tester_id: "f".repeat(32), order: [["a3", "a1", "a2"], ["o2", "o1"]] };
  const body = voteBody(page, session, 0, " Amina ", "B", " good ");
  assert.deepEqual(body, { page: "fr", tester_id: "f".repeat(32), nickname: "Amina", round: "base_fr",
                           item: "ali", clips: ["a3", "a1", "a2"], choice: "B", comment: "good" });
});

test("markdown intros are rendered, and HTML in them is escaped", () => {
  assert.equal(renderMarkdown("# Hi\nUse **A** or *B*."), "<h1>Hi</h1>\n<p>Use <strong>A</strong> or <em>B</em>.</p>");
  assert.equal(renderMarkdown("<script>x</script>"), "<p>&lt;script&gt;x&lt;/script&gt;</p>");
});

test("Arabic and Urdu pages read right to left", () => {
  assert.ok(isRtl("ar") && isRtl("ur"));
  assert.ok(!isRtl("fr") && !isRtl("hi"));
});
