import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReviewReportCard } from "@/components/review-report-card";

describe("ReviewReportCard", () => {
  it("renders", () => {
    const { container } = render(
      <ReviewReportCard appName="Auth SDK" period="Oct 2026" total={50} avgRating={4.2}
        fiveStarCount={25} oneStarCount={3} responseRate={80}
        highlights={[{ text: "Amazing!", rating: 5 }]}
        concerns={[{ text: "Crashes.", rating: 1 }]} />
    );
    expect(container.textContent).toContain("Auth SDK — Review Report");
    expect(container.textContent).toContain("Oct 2026");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("⭐ 4.2");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Crashes.");
  });
});
