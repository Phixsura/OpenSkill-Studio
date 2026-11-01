import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CapabilityRegistryCard from "../src/components/capability-registry-card";

const caps = [
  {
    capability_id: "webhooks",
    name: "Webhooks",
    version: "2.0.0",
    description: "Send and receive webhooks",
  },
  { capability_id: "oauth", name: "OAuth 2.0", version: "1.0.0", description: "" },
  {
    capability_id: "analytics",
    name: "Analytics",
    version: "3.1.0",
    description: "Usage analytics",
  },
];

describe("CapabilityRegistryCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<CapabilityRegistryCard capabilities={caps} appName="My App" />);
    expect(container.textContent).toContain("Capabilities");
    expect(container.textContent).toContain("My App");
  });

  it("shows declared count", () => {
    const { container } = render(<CapabilityRegistryCard capabilities={caps} appName="App" />);
    expect(container.textContent).toContain("3 declared");
  });

  it("renders capability names and versions", () => {
    const { container } = render(<CapabilityRegistryCard capabilities={caps} appName="App" />);
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("OAuth 2.0");
  });

  it("shows descriptions", () => {
    const { container } = render(<CapabilityRegistryCard capabilities={caps} appName="App" />);
    expect(container.textContent).toContain("Send and receive webhooks");
  });

  it("shows empty state", () => {
    const { container } = render(<CapabilityRegistryCard capabilities={[]} appName="App" />);
    expect(container.textContent).toContain("No capabilities declared");
  });
});
