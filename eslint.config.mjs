import eslint from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import eslintConfigPrettier from 'eslint-config-prettier';

export default tseslint.config(
  {
    files: ['**/*.{js,ts}'],
  },
  {
    ignores: ['jest.config.js', '**/node_modules/**', '**/.venv/**', 'cdk.out/**'],
  },
  { languageOptions: { globals: globals.browser } },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  eslintConfigPrettier
);
