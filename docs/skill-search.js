(async function () {
  const form = document.getElementById('skillSearchForm');
  const input = document.getElementById('skillSearchInput');
  const status = document.getElementById('skillSearchStatus');
  const universe = document.querySelector('.workflow-universe');
  const queryCard = document.getElementById('animatedQuery');
  const serverStatus = document.getElementById('animatedSearchStatus');
  const resultList = document.getElementById('animatedSkillResults');
  if (!form || !input || !status || !universe || !queryCard || !serverStatus || !resultList) return;

  const tokenize = (text) => text.toLowerCase().match(/[\p{L}\p{N}_+#.-]+/gu) || [];
  const terms = (text) => [...new Set(tokenize(text).filter((term) => term.length > 1))];
  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const wait = (milliseconds) => new Promise((resolve) => window.setTimeout(resolve, milliseconds));
  let skills = [];

  try {
    const response = await fetch('skills-index.json');
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const payload = await response.json();
    skills = payload.skills || [];
    status.textContent = skills.length + ' indexed skills · browser-local BM25 · Top-3';
  } catch (error) {
    status.textContent = 'Could not load the skill index. Open this page through the local web server.';
    form.querySelector('button').disabled = true;
    return;
  }

  const documents = skills.map((skill) => terms(skill.search_text || (skill.name + ' ' + skill.description)));
  const documentFrequency = new Map();
  documents.forEach((tokens) => new Set(tokens).forEach((token) => {
    documentFrequency.set(token, (documentFrequency.get(token) || 0) + 1);
  }));
  const averageLength = documents.reduce((sum, tokens) => sum + tokens.length, 0) / Math.max(1, documents.length);
  const k1 = 1.2;
  const b = 0.75;

  function search(query) {
    const queryTerms = terms(query);
    if (!queryTerms.length) return [];
    return skills.map((skill, index) => {
      const tokens = documents[index];
      const counts = new Map();
      tokens.forEach((token) => counts.set(token, (counts.get(token) || 0) + 1));
      const lengthNorm = 1 - b + b * (tokens.length / Math.max(1, averageLength));
      let score = 0;
      queryTerms.forEach((term) => {
        const frequency = counts.get(term) || 0;
        if (!frequency) return;
        const df = documentFrequency.get(term) || 0;
        const idf = Math.log(1 + (skills.length - df + 0.5) / (df + 0.5));
        score += idf * ((frequency * (k1 + 1)) / (frequency + k1 * lengthNorm));
      });
      return { skill, score };
    }).filter((item) => item.score > 0).sort((left, right) => right.score - left.score).slice(0, 3);
  }

  function render(matches) {
    if (!matches.length) {
      resultList.innerHTML = '<li class="no-skill-match"><span><b>No direct matches</b><small>Try a more specific English query</small></span></li>';
      return;
    }
    resultList.innerHTML = matches.map(({ skill, score }) => '<li><span><b>' + escapeHtml(skill.name) + '</b><small>' + escapeHtml(skill.category) + '</small></span><strong><em>BM25</em>' + score.toFixed(2) + '</strong></li>').join('');
  }

  async function runSearch(event) {
    if (event) event.preventDefault();
    const query = input.value.trim();
    if (!query || universe.classList.contains('search-running')) return;
    const button = form.querySelector('button');
    button.disabled = true;
    queryCard.textContent = query;
    resultList.classList.add('results-pending');
    universe.classList.remove('stage-search', 'stage-results', 'stage-agent');
    void universe.offsetWidth;
    universe.classList.add('search-running');
    serverStatus.textContent = 'Receiving coding query';
    await wait(650);
    universe.classList.add('stage-search');
    serverStatus.textContent = 'Searching 993 skills · matching · ranking';
    const matches = search(query);
    await wait(1050);
    render(matches);
    resultList.classList.remove('results-pending');
    universe.classList.add('stage-results');
    serverStatus.textContent = matches.length ? 'Top-3 skills retrieved' : 'No direct keyword matches';
    await wait(850);
    universe.classList.add('stage-agent');
    await wait(900);
    universe.classList.remove('search-running', 'stage-search', 'stage-results', 'stage-agent');
    button.disabled = false;
  }

  form.addEventListener('submit', runSearch);
  runSearch();
}());
