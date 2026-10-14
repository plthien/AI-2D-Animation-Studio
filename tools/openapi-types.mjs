import { readFile, writeFile } from 'node:fs/promises';
import process from 'node:process';
import openapiTS, { astToString } from 'openapi-typescript';

const source = new URL('../openapi.json', import.meta.url);
const destination = new URL('../src/api/generated.ts', import.meta.url);
const schema = JSON.parse(await readFile(source, 'utf8'));
const generated = astToString(await openapiTS(schema));

if (process.argv.includes('--check')) {
  const current = await readFile(destination, 'utf8').catch(() => '');
  if (current !== generated) {
    console.error('Generated API types are stale. Run npm run generate:api-types.');
    process.exitCode = 1;
  } else {
    console.log('Generated API types match openapi.json.');
  }
} else {
  await writeFile(destination, generated, 'utf8');
  console.log('Wrote src/api/generated.ts');
}
