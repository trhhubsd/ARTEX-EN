import packageJson from "../../package.json";

const currentYear = new Date().getFullYear();

export const APP_CONFIG = {
  name: "ARTEX",
  version: packageJson.version,
  copyright: `© ${currentYear}, ARTEX.`,
  meta: {
    title: "ARTEX: Autonomous Penetration Testing Console",
    description: "LLM Driver-Based Autonomous Penetration Testing System Console",
  },
};
