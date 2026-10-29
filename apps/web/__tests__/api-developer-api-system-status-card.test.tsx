import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPISystemStatusCard from "../src/components/api-developer-api-system-status-card";

const comps = [{ name: "API", status: "operational" }, { name: "Database", status: "degraded" }];

describe("APIDeveloperAPISystemStatusCard", () => {
  it("shows status", () => {
    const { container } = render(<APIDeveloperAPISystemStatusCard components={comps} overall="partial_degradation" activeIncidents={1} appName="App" />);
    expect(container.textContent).toContain("System Status");
    expect(container.textContent).toContain("partial degradation");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("degraded");
  });
});
