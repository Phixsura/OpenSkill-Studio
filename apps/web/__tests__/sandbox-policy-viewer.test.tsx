import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxPolicyViewer } from "@/components/sandbox-policy-viewer";

const MOCK_POLICY = {
  app_id: "app-1",
  network_rules: [
    { domain: "api.example.com", action: "allow" as const, protocols: ["https"] },
    { domain: "evil.com", action: "deny" as const, protocols: ["https", "http"] },
  ],
  filesystem_rules: [
    { path_prefix: "/tmp/sandbox/", readable: true, writable: true, max_file_bytes: 10485760 },
    { path_prefix: "/data/readonly/", readable: true, writable: false, max_file_bytes: 5242880 },
  ],
  allowed_env_vars: ["NODE_ENV", "TZ", "API_URL"],
  allowed_secret_keys: ["API_KEY", "DB_PASSWORD"],
  max_execution_seconds: 60,
  max_memory_mb: 256,
  allow_subprocess: false,
  network_default: "deny" as const,
};

describe("SandboxPolicyViewer", () => {
  it("renders heading and app name", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="My App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("Sandbox Policy");
    expect(container.textContent).toContain("My App");
  });

  it("renders resource limits", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("60s");
    expect(container.textContent).toContain("256 MB");
    expect(container.textContent).toContain("Deny"); // subprocess
  });

  it("renders network rules", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("evil.com");
    expect(container.textContent).toContain("Allow");
  });

  it("renders network default", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("Deny");
  });

  it("renders filesystem rules", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("/tmp/sandbox/");
    expect(container.textContent).toContain("/data/readonly/");
    expect(container.textContent).toContain("R✓");
    expect(container.textContent).toContain("W✗");
  });

  it("renders env var chips", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("NODE_ENV");
    expect(container.textContent).toContain("TZ");
    expect(container.textContent).toContain("API_URL");
  });

  it("renders secret key chips", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("DB_PASSWORD");
  });

  it("shows Org Override badge", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={true} />,
    );
    expect(container.textContent).toContain("Org Override Active");
  });

  it("hides Org Override badge when not active", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).not.toContain("Org Override");
  });

  it("shows None for empty env vars", () => {
    const empty = { ...MOCK_POLICY, allowed_env_vars: [] };
    const { container } = render(
      <SandboxPolicyViewer policy={empty} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("None");
  });

  it("shows no-rules message for empty network", () => {
    const empty = { ...MOCK_POLICY, network_rules: [] };
    const { container } = render(
      <SandboxPolicyViewer policy={empty} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("No rules");
  });

  it("formats file size", () => {
    const { container } = render(
      <SandboxPolicyViewer policy={MOCK_POLICY} appName="App" hasOrgOverride={false} />,
    );
    expect(container.textContent).toContain("10 MB");
    expect(container.textContent).toContain("5 MB");
  });
});
