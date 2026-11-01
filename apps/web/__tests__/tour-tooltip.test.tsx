import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TourTooltip } from "@/components/tour-tooltip";

describe("TourTooltip", () => {
  it("renders tooltip", () => {
    const onNext = vi.fn();
    const { container, getByText } = render(
      <TourTooltip step={{ id: "welcome", title: "Welcome!", body: "Let's go", position: "bottom" }}
        currentIndex={0} totalSteps={5} onNext={onNext} onSkip={vi.fn()} />
    );
    expect(container.textContent).toContain("Welcome!");
    expect(container.textContent).toContain("Let's go");
    expect(container.textContent).toContain("1/5");
    expect(container.textContent).toContain("Next");
    fireEvent.click(getByText("Next"));
    expect(onNext).toHaveBeenCalled();
  });

  it("shows Finish on last step", () => {
    const { container } = render(
      <TourTooltip step={{ id: "done", title: "Done!", body: "All set", position: "center" }}
        currentIndex={4} totalSteps={5} onNext={vi.fn()} onSkip={vi.fn()} />
    );
    expect(container.textContent).toContain("Finish");
  });
});
