const fs = require('fs');
const html = fs.readFileSync('D:/BursztynDesktop/tomo-desktop/src/index.html', 'utf8');
const ids = [...html.matchAll(/id="([^"]+)"/g)].map((m) => m[1]);
const set = new Set(ids);
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));
const refs = [...script.matchAll(/\$\('([^']+)'\)\.(onclick|innerHTML|oninput|onchange)/g)];
const missing = [];
for (const m of refs) {
  if (!set.has(m[1])) missing.push(m[0] + ' -> #' + m[1]);
}
console.log('missing', missing.length ? missing.join('\n') : 'none');
