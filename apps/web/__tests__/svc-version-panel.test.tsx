import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcVersionPanel } from "@/components/svc-version-panel";
describe("SvcVersionPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SvcVersionPanel envs={["prod", "staging"]} inconsistentCount={1}
        rows={[
          { service: "api", prod: "2.0", staging: "2.1" },
          { service: "web", prod: "3.0", staging: "3.0" },
        ]} />
    );
    expect(container.textContent).toContain("Service Versions");
    expect(container.textContent).toContain("1 inconsistent");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("2.1");
  });
});
