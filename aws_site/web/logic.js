// The listening test's logic, kept apart from the page so it can be tested with node --test.
//   rounds/pages.json lists the pages (one per language) and the rounds each one shows.
//   A round that has not been built yet is skipped, and a page with no rounds is left out.

// Players are labelled A to E in the order a visitor sees them.
export const LETTERS = "ABCDE";

export function buildPages(config, rounds) {
  const pages = [];
  for (const p of config.pages) {
    const page = { path: p.path, name: p.name, language: p.language, intro: p.intro || "", questions: [] };
    for (const r of p.rounds) {
      const info = rounds[r.round];
      if (!info) continue;
      for (const it of info.items) {
        if (it.clips.length < 2 || it.clips.length > LETTERS.length) {
          throw new Error(`${r.round}/${it.item} has ${it.clips.length} clips; the page shows 2 to 5.`);
        }
        page.questions.push({
          round: r.round, item: it.item, label: it.label,
          question: r.question || info.question, heading: r.heading, same_label: r.same_label,
          clips: it.clips, text: it.text || "", hint: it.hint || "",
        });
      }
    }
    if (page.questions.length) pages.push(page);
  }
  return pages;
}

function shuffled(list, random) {
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

export function randomHex32() {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

// A random tester id and a random clip order per question.
export function newSession(page, random = Math.random, makeId = randomHex32) {
  return { tester_id: makeId(), order: page.questions.map((q) => shuffled(q.clips, random)) };
}

// What the page sends to POST /api/vote for question number `index`.
export function voteBody(page, session, index, nickname, choice, comment) {
  const q = page.questions[index];
  return {
    page: page.language, tester_id: session.tester_id, nickname: (nickname || "").trim(),
    round: q.round, item: q.item, clips: session.order[index], choice, comment: (comment || "").trim(),
  };
}

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Just enough Markdown for the intros: # headings, **bold**, *italic*, one paragraph per line.
export function renderMarkdown(text) {
  return text.split("\n").filter((line) => line.trim()).map((line) => {
    const html = escapeHtml(line.trim())
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>");
    const heading = html.match(/^(#{1,3}) (.*)$/);
    if (heading) return `<h${heading[1].length}>${heading[2]}</h${heading[1].length}>`;
    return `<p>${html}</p>`;
  }).join("\n");
}

export function isRtl(language) {
  return language === "ar" || language === "ur";
}
