import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import type {
  ExtensionAPI,
  ProviderConfig,
  ProviderModelConfig,
} from "@earendil-works/pi-coding-agent";

type CatalogModel = Partial<ProviderModelConfig> & Pick<ProviderModelConfig, "id">;
type CatalogProvider = Omit<ProviderConfig, "models"> & {
  models?: CatalogModel[];
};

export default function (pi: ExtensionAPI) {
  const agentDir =
    process.env.PI_CODING_AGENT_DIR ?? join(homedir(), ".pi", "agent");
  const catalogPath = [
    join(process.cwd(), ".pi", "models.json"),
    join(agentDir, "models.json"),
  ].find((path) => existsSync(path));

  if (!catalogPath) return;

  const { providers } = JSON.parse(readFileSync(catalogPath, "utf8")) as {
    providers: Record<string, CatalogProvider>;
  };

  for (const [name, config] of Object.entries(providers)) {
    const models = config.models?.map((model) => ({
      name: model.id,
      reasoning: false,
      input: ["text"],
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: 128000,
      maxTokens: 16384,
      ...model,
    }));

    pi.registerProvider(name, { ...config, models } as ProviderConfig);
  }
}
