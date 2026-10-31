import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SetupProgressCard } from "@/components/setup-progress-card";

describe("SetupProgressCard", () => {
  const steps = [
    { id: "basic", title: "Basic Info", description: "", required: true, completed: true },
    { id: "perms", title: "Permissions", description: "", required: true, completed: false },
  ];
  it("renders progress", () => {
    const { container } = render(
      <SetupProgressCard steps={steps} progressPct={50} readyToPublish={false}
        nextStep={steps[1]} onComplete={vi.fn()} />
    );
    expect(container.textContent).toContain("App Setup");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Basic Info");
    expect(container.textContent).toContain("Permissions");
    expect(container.textContent).toContain("Start");
  });
});
