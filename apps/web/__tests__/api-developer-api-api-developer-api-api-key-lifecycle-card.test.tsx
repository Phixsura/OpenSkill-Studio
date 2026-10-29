import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiKeyLifecycleCard from "../src/components/api-developer-api-api-developer-api-api-key-lifecycle-card";

const keys = [
  { key_id: "k1", name: "Production", prefix: "sk-prod-", status: "active", usage_count: 50000 },
  { key_id: "k2", name: "Old Key", prefix: "sk-old--", status: "revoked", usage_count: 10000 },
];

describe("APIDeveloperAPIApiDeveloperApiApiKeyLifecycleCard", () => {
  it("shows keys", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiKeyLifecycleCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("Key Lifecycle");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("sk-prod-");
    expect(container.textContent).toContain("50,000 uses");
    expect(container.textContent).toContain("revoked");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiKeyLifecycleCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No API keys");
  });
});
