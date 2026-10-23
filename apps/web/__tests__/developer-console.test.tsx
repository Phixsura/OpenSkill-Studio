import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperConsole } from "@/components/developer-console";

describe("DeveloperConsole", () => {
  const sections = [{ id: "apps", label: "My Apps", icon: "📦", count: 5, href: "/apps" }];
  const stats = [{ label: "Apps", value: 5, icon: "📦" }];
  it("renders console", () => {
    const { container } = render(
      <DeveloperConsole greeting="Good morning, Alice!" sections={sections} stats={stats}
        orgName="Acme" orgPlan="pro" notifications={3} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("Good morning, Alice!");
    expect(container.textContent).toContain("Acme");
    expect(container.textContent).toContain("My Apps");
    expect(container.textContent).toContain("3 🔔");
  });
});
