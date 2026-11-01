import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiConfigManagerCard from "../src/components/api-developer-api-api-developer-api-config-manager-card";

describe("APIDeveloperAPIApiDeveloperApiConfigManagerCard", () => {
  it("shows config", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiConfigManagerCard config={{ rate_limit: 1000, debug: false }} version={5} historyCount={3} appName="App" />);
    expect(container.textContent).toContain("Config Manager");
    expect(container.textContent).toContain("v5");
    expect(container.textContent).toContain("rate_limit");
    expect(container.textContent).toContain("1000");
    expect(container.textContent).toContain("3 snapshots");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiConfigManagerCard config={{}} version={0} historyCount={0} appName="App" />);
    expect(container.textContent).toContain("No config values");
  });
});
