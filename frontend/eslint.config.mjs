import tsParser from "@typescript-eslint/parser";

export default [
  {
    ignores: [".next/**", "out/**", "build/**", "next-env.d.ts"],
  },
  {
    files: ["**/*.{js,mjs,ts,tsx}"],
    languageOptions: {
      parser: tsParser,
    },
    rules: {
      "no-console": "warn",
      "no-unused-vars": "off",
    },
  },
];
