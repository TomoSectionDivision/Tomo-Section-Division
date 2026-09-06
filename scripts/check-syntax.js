const fs = require('fs');
const s = fs.readFileSync('D:/BursztynDesktop/tomo-desktop/src/index.html', 'utf8');
const start = s.indexOf('<script>');
const end = s.lastIndexOf('</script>');
if (start < 0 || end < 0) {
  console.log('no script');
  process.exit(1);
}
const code = s.slice(start + 8, end);
try {
  new Function(code);
  console.log('syntax OK', code.length);
} catch (e) {
  console.error('SYNTAX ERROR:', e.message);
  process.exit(1);
}
