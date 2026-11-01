import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingChecklist } from "@/components/onboarding-checklist";

const items = [
  { itemId: "profile", title: "Complete Profile", description: "Add bio", completed: true, required: true },
  { itemId: "api_key", title: "Generate API Key", description: "Create key", completed: false, required: true },
];
const progress = { total: 2, completed: 1, percentage: 50 };

describe("OnboardingChecklist", () => {
  it("renders checklist", () => {
    const { container } = render(<OnboardingChecklist items={items} progress={progress} />);
    expect(container.textContent).toContain("Complete Profile");
    expect(container.textContent).toContain("1/2 (50%)");
    expect(container.textContent).toContain("required");
  });
  it("complete item", () => {
    const fn = vi.fn();
    const { container } = render(<OnboardingChecklist items={items} progress={progress} onComplete={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]); // api_key not completed
    expect(fn).toHaveBeenCalledWith("api_key");
  });
});
