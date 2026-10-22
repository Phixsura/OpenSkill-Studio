import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperPortalLayout } from "@/components/developer-portal-layout";

const ACTIONS = [{ label: "Create App", icon: "➕", href: "/new" }, { label: "Docs", icon: "📖", href: "/docs" }];

describe("DeveloperPortalLayout", () => {
  it("shows welcome", () => {
    const { container } = render(<DeveloperPortalLayout developerName="Alice" isNew={true} appCount={0} quickActions={ACTIONS}><p>Content</p></DeveloperPortalLayout>);
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("Content");
  });
  it("shows quick actions", () => {
    const { container } = render(<DeveloperPortalLayout developerName="Bob" isNew={false} appCount={5} quickActions={ACTIONS}><div /></DeveloperPortalLayout>);
    expect(container.textContent).toContain("Create App");
    expect(container.textContent).toContain("Docs");
  });
});
