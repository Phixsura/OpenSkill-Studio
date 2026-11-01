import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-shadow-mode-card";

describe("RequestShadowModeCard", () => {
  it("shows shadow configs", () => {
    const configs = [{ endpoint: "/users", method: "GET", shadow_version: "v2", active: true }];
    const { container } = render(<Card configs={configs} matchRate={98.5} mismatchCount={3} appName="App" />);
    expect(container.textContent).toContain("Shadow Mode");
    expect(container.textContent).toContain("98.5% match");
    expect(container.textContent).toContain("3 mismatches");
    expect(container.textContent).toContain("→ v2");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} matchRate={0} mismatchCount={0} appName="App" />);
    expect(container.textContent).toContain("No shadow configs");
  });
});
