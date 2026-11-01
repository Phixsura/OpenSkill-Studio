import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyCreationWizard } from "@/components/key-creation-wizard";

describe("KeyCreationWizard", () => {
  it("renders wizard", () => {
    const { container } = render(
      <KeyCreationWizard onCreate={vi.fn()} scopes={[
        { id: "read:apps", label: "Read Apps", description: "View apps", risk: "low" },
        { id: "deploy", label: "Deploy", description: "Deploy apps", risk: "high" },
      ]} />
    );
    expect(container.textContent).toContain("Create API Key");
    expect(container.textContent).toContain("Read Apps");
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("low");
    expect(container.textContent).toContain("high");
  });
});
