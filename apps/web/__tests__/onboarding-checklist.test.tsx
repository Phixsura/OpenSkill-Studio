import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingChecklist } from "@/components/onboarding-checklist";

describe("OnboardingChecklist", () => {
  const tasks = [
    { id: "1", title: "Create app", description: "Set up your first app", completed: true, action_url: null, icon: "🔧", required: true },
    { id: "2", title: "Add webhook", description: "", completed: false, action_url: null, icon: "🔗", required: true },
  ];
  it("renders tasks", () => {
    const { container } = render(
      <OnboardingChecklist tasks={tasks} greeting="Welcome!" progressPct={50} onComplete={vi.fn()} />
    );
    expect(container.textContent).toContain("Welcome!");
    expect(container.textContent).toContain("Create app");
    expect(container.textContent).toContain("Add webhook");
    expect(container.textContent).toContain("50%");
  });
  it("complete click", () => {
    const fn = vi.fn();
    const { container } = render(
      <OnboardingChecklist tasks={tasks} greeting="Hi" progressPct={50} onComplete={fn} />
    );
    const buttons = container.querySelectorAll("button");
    fireEvent.click(buttons[1]); // second task (uncompleted)
    expect(fn).toHaveBeenCalledWith("2");
  });
});
