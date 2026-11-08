// The listening test page: loads the rounds, shows one page per language, and saves each
// answer to POST /api/vote as soon as it is given. Progress is kept in this browser, so a
// tester can close the page and continue later. The logic lives in logic.js (tested).
import { LETTERS, buildPages, isRtl, newSession, renderMarkdown, voteBody } from "./logic.js";

// Interface words per language. Non-English entries are drafts for native review.
const UI = {
  en: { back: "All languages", name: "Your name or nickname (optional)", nameHint: "Only so we can thank you. Leave empty to stay anonymous.",
        answered: "{n} of {total} answered", comment: "Comment (optional)", commentLine: "Did any of them skip or mispronounce words? (optional)",
        saving: "Saving…", saved: "Saved", failed: "Not saved.", retry: "Try again",
        doneTitle: "Thank you!", doneText: "All your answers are saved. You can still change any of them.",
        landing: "Help us choose the voices for QuranLingo", landingText: "Choose your language. Headphones recommended.",
        loadError: "The test could not be loaded. Please refresh the page." },
  fr: { back: "Toutes les langues", name: "Votre nom ou pseudo (facultatif)", nameHint: "Seulement pour vous remercier. Laissez vide pour rester anonyme.",
        answered: "{n} sur {total} répondues", comment: "Commentaire (facultatif)", commentLine: "Un mot a-t-il été sauté ou mal prononcé ? (facultatif)",
        saving: "Enregistrement…", saved: "Enregistré", failed: "Non enregistré.", retry: "Réessayer",
        doneTitle: "Merci !", doneText: "Toutes vos réponses sont enregistrées. Vous pouvez encore les modifier." },
  de: { back: "Alle Sprachen", name: "Ihr Name oder Spitzname (optional)", nameHint: "Nur damit wir uns bedanken können. Leer lassen, um anonym zu bleiben.",
        answered: "{n} von {total} beantwortet", comment: "Kommentar (optional)", commentLine: "Wurden Wörter ausgelassen oder falsch ausgesprochen? (optional)",
        saving: "Wird gespeichert…", saved: "Gespeichert", failed: "Nicht gespeichert.", retry: "Erneut versuchen",
        doneTitle: "Vielen Dank!", doneText: "Alle Antworten sind gespeichert. Sie können sie noch ändern." },
  tr: { back: "Tüm diller", name: "Adınız veya takma adınız (isteğe bağlı)", nameHint: "Yalnızca teşekkür etmek için. Anonim kalmak için boş bırakın.",
        answered: "{total} sorudan {n} tanesi yanıtlandı", comment: "Yorum (isteğe bağlı)", commentLine: "Atlanan veya yanlış okunan kelime var mı? (isteğe bağlı)",
        saving: "Kaydediliyor…", saved: "Kaydedildi", failed: "Kaydedilemedi.", retry: "Tekrar dene",
        doneTitle: "Teşekkürler!", doneText: "Tüm yanıtlarınız kaydedildi. Hâlâ değiştirebilirsiniz." },
  ar: { back: "كل اللغات", name: "اسمك أو لقبك (اختياري)", nameHint: "فقط لنشكرك. اتركه فارغًا لتبقى مجهول الهوية.",
        answered: "تمت الإجابة عن {n} من {total}", comment: "تعليق (اختياري)", commentLine: "هل تم تخطي أي كلمة أو نطقها بشكل خاطئ؟ (اختياري)",
        saving: "جارٍ الحفظ…", saved: "تم الحفظ", failed: "لم يتم الحفظ.", retry: "حاول مرة أخرى",
        doneTitle: "شكرًا لك!", doneText: "تم حفظ جميع إجاباتك. لا يزال بإمكانك تغيير أي منها." },
  hi: { back: "सभी भाषाएँ", name: "आपका नाम या उपनाम (वैकल्पिक)", nameHint: "सिर्फ़ धन्यवाद कहने के लिए। गुमनाम रहने के लिए खाली छोड़ दें।",
        answered: "{total} में से {n} के उत्तर दिए", comment: "टिप्पणी (वैकल्पिक)", commentLine: "क्या कोई शब्द छूटा या गलत बोला गया? (वैकल्पिक)",
        saving: "सहेजा जा रहा है…", saved: "सहेजा गया", failed: "सहेजा नहीं गया।", retry: "फिर से कोशिश करें",
        doneTitle: "धन्यवाद!", doneText: "आपके सभी उत्तर सहेज लिए गए हैं। आप अब भी इन्हें बदल सकते हैं।" },
  ur: { back: "تمام زبانیں", name: "آپ کا نام یا عرفیت (اختیاری)", nameHint: "صرف شکریہ ادا کرنے کے لیے۔ گمنام رہنے کے لیے خالی چھوڑ دیں۔",
        answered: "{total} میں سے {n} کے جواب دیے گئے", comment: "تبصرہ (اختیاری)", commentLine: "کیا کوئی لفظ چھوٹ گیا یا غلط بولا گیا؟ (اختیاری)",
        saving: "محفوظ کیا جا رہا ہے…", saved: "محفوظ ہو گیا", failed: "محفوظ نہیں ہوا۔", retry: "دوبارہ کوشش کریں",
        doneTitle: "شکریہ!", doneText: "آپ کے تمام جوابات محفوظ ہو گئے ہیں۔ آپ اب بھی انہیں بدل سکتے ہیں۔" },
};
const t = (lang, key) => (UI[lang] && UI[lang][key]) || UI.en[key];

const app = document.getElementById("app");

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v; // only used with renderMarkdown output, which escapes HTML
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children) if (c != null) node.append(c);
  return node;
}

async function loadJson(url) {
  const response = await fetch(url, { cache: "no-cache" });
  return response.ok ? response.json() : null;
}

// Browser storage can be unavailable (private windows); the test still works, it just will not resume.
const store = {
  get(key) { try { return JSON.parse(localStorage.getItem(key)); } catch { return null; } },
  set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* ignore */ } },
};

function signature(page) {
  return page.questions.map((q) => `${q.round}#${q.item}:${q.clips.join(",")}`).join("|");
}

function loadState(page) {
  const key = `quranlingo-voices:${page.path}`;
  const saved = store.get(key);
  const state = saved && saved.signature === signature(page)
    ? saved
    : { signature: signature(page), session: newSession(page), answers: {}, nickname: store.get("quranlingo-voices:nickname") || "" };
  return { key, state };
}

function renderLanding(pages) {
  document.documentElement.lang = "en";
  document.documentElement.dir = "ltr";
  app.replaceChildren(
    el("h1", {}, t("en", "landing")),
    el("p", {}, t("en", "landingText")),
    el("ul", { class: "languages" }, ...pages.map((p) =>
      el("li", {}, el("a", { href: `#/${p.path}` }, p.name, el("small", {}, `${p.questions.length} questions`))))),
  );
}

function renderPage(page) {
  const lang = page.language;
  document.documentElement.lang = lang;
  document.documentElement.dir = isRtl(lang) ? "rtl" : "ltr";
  const { key, state } = loadState(page);
  const persist = () => store.set(key, state);
  persist();

  const total = page.questions.length;
  const fill = el("div", { class: "fill" });
  const count = el("div", { class: "count" });
  const done = el("section", { class: "done", hidden: "" }, el("h2", {}, t(lang, "doneTitle")), el("p", {}, t(lang, "doneText")));
  const updateProgress = () => {
    const n = Object.values(state.answers).filter((a) => a.choice).length;
    fill.style.width = `${(100 * n) / total}%`;
    count.textContent = t(lang, "answered").replace("{n}", n).replace("{total}", total);
    done.hidden = n < total;
  };

  const nameInput = el("input", { type: "text", maxlength: "60", autocomplete: "nickname", value: state.nickname });
  nameInput.addEventListener("input", () => {
    state.nickname = nameInput.value;
    store.set("quranlingo-voices:nickname", state.nickname);
    persist();
  });

  async function save(index, status) {
    const answer = state.answers[index];
    if (!answer || !answer.choice) return;
    status.className = "status";
    status.textContent = t(lang, "saving");
    try {
      const response = await fetch("api/vote", {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify(voteBody(page, state.session, index, state.nickname, answer.choice, answer.comment)),
      });
      if (!response.ok) throw new Error(String(response.status));
      answer.saved = true;
      status.className = "status saved";
      status.textContent = `✓ ${t(lang, "saved")}`;
    } catch {
      answer.saved = false;
      status.className = "status failed";
      status.replaceChildren(`${t(lang, "failed")} `, el("button", { type: "button", onclick: () => save(index, status) }, t(lang, "retry")));
    }
    persist();
  }

  const sections = [];
  let heading = null;
  page.questions.forEach((q, index) => {
    if (q.heading !== heading) {
      heading = q.heading;
      sections.push(el("h2", {}, q.heading));
    }
    const shown = state.session.order[index];
    const letters = LETTERS.slice(0, shown.length);
    const answer = state.answers[index] || (state.answers[index] = { choice: "", comment: "" });
    const status = el("div", { class: answer.saved ? "status saved" : "status" }, answer.saved ? `✓ ${t(lang, "saved")}` : "");
    const card = el("article", { class: answer.choice ? "card answered" : "card" });

    const buttons = [...letters, "same"].map((value) => el("button", {
      type: "button", "aria-pressed": String(answer.choice === value),
      onclick: () => {
        answer.choice = value;
        buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.value === value)));
        card.classList.add("answered");
        updateProgress();
        save(index, status);
      },
    }, value === "same" ? q.same_label : value));
    buttons.forEach((b, i) => { b.dataset.value = [...letters, "same"][i]; });

    const comment = el("textarea", { rows: "1", maxlength: "2000" });
    comment.value = answer.comment;
    comment.addEventListener("input", () => { answer.comment = comment.value; persist(); });
    comment.addEventListener("change", () => save(index, status));

    card.append(
      el("h3", {}, q.label),
      q.text ? el("p", { class: "text" }, `“${q.text}”`) : null,
      q.hint ? el("p", { class: "hint" }, q.hint) : null,
      el("div", { class: "players" }, ...shown.map((clip, i) => el("div", { class: "player" },
        el("span", { class: "letter", "aria-hidden": "true" }, letters[i]),
        el("audio", { controls: "", preload: "none", src: `rounds/${q.round}/${clip}.wav`, "aria-label": letters[i] })))),
      el("p", { class: "question" }, q.question),
      el("div", { class: "choices", role: "group", "aria-label": q.question }, ...buttons),
      el("label", { class: "comment" }, q.text ? t(lang, "commentLine") : t(lang, "comment"), comment),
      status,
    );
    sections.push(card);
  });

  app.replaceChildren(
    el("a", { class: "back", href: "#/" }, `${isRtl(lang) ? "→" : "←"} ${t(lang, "back")}`),
    el("div", { class: "intro", html: renderMarkdown(page.intro) }),
    el("label", { class: "name" }, t(lang, "name"), nameInput, el("small", {}, t(lang, "nameHint"))),
    el("div", { class: "progress" }, el("div", { class: "bar" }, fill), count),
    ...sections,
    done,
  );
  updateProgress();
  window.scrollTo(0, 0);
}

// Only one clip plays at a time.
document.addEventListener("play", (event) => {
  for (const audio of document.querySelectorAll("audio")) if (audio !== event.target) audio.pause();
}, true);

async function main() {
  try {
    const config = await loadJson("rounds/pages.json");
    const names = [...new Set(config.pages.flatMap((p) => p.rounds.map((r) => r.round)))];
    const rounds = {};
    await Promise.all(names.map(async (name) => {
      const info = await loadJson(`rounds/${name}/round.json`).catch(() => null);
      if (info) rounds[name] = info;
    }));
    const pages = buildPages(config, rounds);
    const route = () => {
      const path = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
      const page = pages.find((p) => p.path === path);
      if (page) renderPage(page); else renderLanding(pages);
    };
    window.addEventListener("hashchange", route);
    route();
  } catch (error) {
    app.replaceChildren(el("p", { class: "error" }, t("en", "loadError")));
    console.error(error);
  }
}

main();
