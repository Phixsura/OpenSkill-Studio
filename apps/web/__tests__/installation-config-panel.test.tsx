import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallationConfigPanel } from "@/components/installation-config-panel";

describe("InstallationConfigPanel", () => {
  it("renders config with schema", () => {
    const { container } = render(
      <InstallationConfigPanel
        config={{ base_url: "https://api.example.com" }}
        configSchema={{ properties: { base_url: { type: "string", description: "API URL" } }, required: ["base_url"] }}
      />
    );
    expect(container.textContent).toContain("base_url");
    expect(container.textContent).toContain("API URL");
  });

  it("shows required marker", () => {
    const { container } = render(
      <InstallationConfigPanel config={{}} configSchema={{ properties: { key: { type: "string" } }, required: ["key"] }} />
    );
    expect(container.textContent).toContain("*");
  });

  it("renders raw config without schema", () => {
    const { container } = render(<InstallationConfigPanel config={{ a: 1, b: "two" }} />);
    expect(container.textContent).toContain('"a"');
  });

  it("shows empty state", () => {
    const { container } = render(<InstallationConfigPanel config={{}} />);
    expect(container.textContent).toContain("No configuration");
  });
});
