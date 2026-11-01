import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuickSetupWizard } from "@/components/quick-setup-wizard";

describe("QuickSetupWizard", () => {
  it("renders setup", () => {
    const { container } = render(
      <QuickSetupWizard appName="My App" language="python"
        install="pip install openskill-sdk" code='client = OpenSkill()'
        apiKey="sk_test_abc" nextSteps={["Webhooks", "Deploy"]} estimatedTime="5 minutes" />
    );
    expect(container.textContent).toContain("Quick Setup: My App");
    expect(container.textContent).toContain("pip install");
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("5 minutes");
  });
});
