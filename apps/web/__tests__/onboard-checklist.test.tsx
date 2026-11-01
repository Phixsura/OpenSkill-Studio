import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardChecklist } from "@/components/onboard-checklist";

describe("OnboardChecklist", () => {
  it("renders checklist", () => {
    const { container } = render(
      <OnboardChecklist progressPct={38} readyToContribute={false} onComplete={vi.fn()}
        items={[
          { id: "account", title: "Create account", category: "setup", required: true, completed: true },
          { id: "mfa", title: "Enable MFA", category: "security", required: true, completed: true },
          { id: "repo", title: "Get repo access", category: "development", required: true, completed: false },
        ]} />
    );
    expect(container.textContent).toContain("Onboarding");
    expect(container.textContent).toContain("38%");
    expect(container.textContent).toContain("In Progress");
    expect(container.textContent).toContain("Create account");
    expect(container.textContent).toContain("Enable MFA");
    expect(container.textContent).toContain("Get repo access");
    expect(container.textContent).toContain("required");
  });
});
