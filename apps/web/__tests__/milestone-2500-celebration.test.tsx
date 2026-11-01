import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone2500Celebration } from "@/components/milestone-2500-celebration";

describe("Milestone2500Celebration", () => {
  it("renders milestone", () => {
    const { container } = render(
      <Milestone2500Celebration
        stats={{ commits: 2500, lines: 216000, files: 7258, services: 1250, components: 1250, tests: 2500, modules: 10 }}
        modules={["Extension SDK", "Sandboxed Apps", "Marketplace", "Automation API", "Ecosystem",
          "Developer Portal", "Security", "Infrastructure", "Observability", "Platform Ops"]} />
    );
    expect(container.textContent).toContain("2,500 Commits");
    expect(container.textContent).toContain("216K");
    expect(container.textContent).toContain("7,258");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("All Modules Operational");
  });
});
