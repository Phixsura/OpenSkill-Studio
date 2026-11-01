import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewCardV2 } from "@/components/review-card-v2";

describe("ReviewCardV2", () => {
  it("renders review", () => {
    const { container } = render(
      <ReviewCardV2 title="Great app!" rating={5} body="Love it" pros={["Fast"]} cons={["No dark mode"]}
        verifiedPurchase={true} helpfulYes={10} helpfulNo={2} onHelpful={vi.fn()} />
    );
    expect(container.textContent).toContain("Great app!");
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("Fast");
    expect(container.textContent).toContain("No dark mode");
  });
  it("helpful vote", () => {
    const fn = vi.fn();
    const { container } = render(
      <ReviewCardV2 title="X" rating={3} body="" pros={[]} cons={[]}
        verifiedPurchase={false} helpfulYes={0} helpfulNo={0} onHelpful={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith(true);
  });
});
