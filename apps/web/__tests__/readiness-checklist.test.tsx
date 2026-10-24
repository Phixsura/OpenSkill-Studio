import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReadinessChecklist } from "@/components/readiness-checklist";

describe("ReadinessChecklist", () => {
  it("renders checklist", () => {
    const { container } = render(
      <ReadinessChecklist launchReady={false} readinessPct={70} criticalPass={5} criticalTotal={7}
        checks={[
          { item: "database", category: "infrastructure", critical: true, ready: true },
          { item: "auth", category: "security", critical: true, ready: false },
          { item: "logging", category: "observability", critical: false, ready: true },
        ]} />
    );
    expect(container.textContent).toContain("Launch Readiness");
    expect(container.textContent).toContain("Not Ready");
    expect(container.textContent).toContain("70%");
    expect(container.textContent).toContain("5/7 critical");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("auth");
  });
});
