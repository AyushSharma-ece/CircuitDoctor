// Postinstall script to guarantee Rollup WASM compatibility under Windows Application Control / Smart App Control
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rollupNativePath = path.resolve(__dirname, '../node_modules/rollup/dist/native.js');

if (fs.existsSync(rollupNativePath)) {
  let content = fs.readFileSync(rollupNativePath, 'utf8');
  if (!content.includes("@rollup/wasm-node/dist/native.js")) {
    const target = `const nativeModule = requireWithFriendlyError(\n\texistsSync(path.join(__dirname, localName)) ? localName : \`@rollup/rollup-\${packageBase}\`\n);`;
    const replacement = `let nativeModule;\ntry {\n\tnativeModule = requireWithFriendlyError(\n\t\texistsSync(path.join(__dirname, localName)) ? localName : \`@rollup/rollup-\${packageBase}\`\n\t);\n} catch (err) {\n\ttry {\n\t\tnativeModule = require('@rollup/wasm-node/dist/native.js');\n\t} catch {\n\t\tthrow err;\n\t}\n}`;
    if (content.includes(target)) {
      content = content.replace(target, replacement);
      fs.writeFileSync(rollupNativePath, content, 'utf8');
      console.log('[CircuitDoctor] Successfully verified Rollup WASM Smart App Control patch.');
    }
  }
}
