import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ApiKeyCard from "../src/components/api-key-card";

const activeKey = {
  key_id: "k1",
  name: "Production Key",
  prefix: "sk_live_",
  scopes: ["read", "write"],
  created_at: new Date(Date.now() - 86_400_000).toISOString(),
  expires_at: new Date(Date.now() + 86_400_000 * 30).toISOString(),
  revoked: false,
  last_used_at: new Date(Date.now() - 3_600_000).toISOString(),
};

const revokedKey = {
  key_id: "k2",
  name: "Old Key",
  prefix: "sk_test_",
  scopes: ["read"],
  created_at: new Date(Date.now() - 86_400_000 * 60).toISOString(),
  expires_at: null,
  revoked: true,
  last_used_at: null,
};

const expiredKey = {
  key_id: "k3",
  name: "Temp Key",
  prefix: "sk_tmp_a",
  scopes: [],
  created_at: new Date(Date.now() - 86_400_000 * 10).toISOString(),
  expires_at: new Date(Date.now() - 86_400_000).toISOString(),
  revoked: false,
  last_used_at: new Date(Date.now() - 86_400_000 * 2).toISOString(),
};

describe("ApiKeyCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ApiKeyCard keys={[activeKey]} appName="My App" />);
    expect(container.textContent).toContain("API Keys");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(<ApiKeyCard keys={[activeKey, revokedKey]} appName="App" />);
    expect(container.textContent).toContain("1 active");
  });

  it("renders key name and prefix", () => {
    const { container } = render(<ApiKeyCard keys={[activeKey]} appName="App" />);
    expect(container.textContent).toContain("Production Key");
    expect(container.textContent).toContain("sk_live_");
  });

  it("shows scope badges", () => {
    const { container } = render(<ApiKeyCard keys={[activeKey]} appName="App" />);
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
  });

  it("shows no-scopes label", () => {
    const { container } = render(<ApiKeyCard keys={[expiredKey]} appName="App" />);
    expect(container.textContent).toContain("No scopes");
  });

  it("shows revoked badge", () => {
    const { container } = render(<ApiKeyCard keys={[revokedKey]} appName="App" />);
    expect(container.textContent).toContain("Revoked");
  });

  it("shows expired badge", () => {
    const { container } = render(<ApiKeyCard keys={[expiredKey]} appName="App" />);
    expect(container.textContent).toContain("Expired");
  });

  it("shows last used time", () => {
    const { container } = render(<ApiKeyCard keys={[activeKey]} appName="App" />);
    expect(container.textContent).toContain("Last used:");
  });

  it("shows never used", () => {
    const { container } = render(<ApiKeyCard keys={[revokedKey]} appName="App" />);
    expect(container.textContent).toContain("Never");
  });

  it("shows empty state", () => {
    const { container } = render(<ApiKeyCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No API keys");
  });
});
