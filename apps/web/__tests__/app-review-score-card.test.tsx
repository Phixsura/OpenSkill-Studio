import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppReviewScoreCard } from "@/components/app-review-score-card";

const GOOD_SCORE = {
  app_id: "app-1",
  composite_score: 87.5,
  grade: "good" as const,
  breakdown: [
    { name: "Description", score: 100, weight: 0.15, details: "220 chars" },
    { name: "Metadata", score: 100, weight: 0.15, details: "4/4 fields" },
    { name: "Security", score: 80, weight: 0.25, details: "3 perms, 0 critical" },
    { name: "Versioning", score: 100, weight: 0.1, details: "v2.1.0" },
    { name: "Publisher Trust", score: 80, weight: 0.15, details: "180d, 5 apps" },
    { name: "Quality", score: 100, weight: 0.1, details: "tests=✓, docs=✓" },
    { name: "Manifest", score: 90, weight: 0.1, details: "18/20" },
  ],
  auto_approve: true,
  flags: [],
};

const POOR_SCORE = {
  app_id: "app-2",
  composite_score: 28.0,
  grade: "poor" as const,
  breakdown: [
    { name: "Description", score: 10, weight: 0.15, details: "6 chars" },
    { name: "Security", score: 20, weight: 0.25, details: "8 perms, 3 critical" },
  ],
  auto_approve: false,
  flags: [
    "Missing app icon",
    "Missing privacy policy",
    "Uses 3 critical permissions — requires security review",
  ],
};

describe("AppReviewScoreCard", () => {
  it("renders app name", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="Great App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Great App");
  });

  it("renders composite score", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("87.5");
  });

  it("renders grade label", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Good");
  });

  it("shows auto-approve banner", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("auto-approval");
  });

  it("hides auto-approve banner when not eligible", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={POOR_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).not.toContain("auto-approval");
  });

  it("renders flags", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={POOR_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Missing app icon");
    expect(container.textContent).toContain("critical permissions");
  });

  it("hides flags section when none", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).not.toContain("Review Flags");
  });

  it("renders breakdown components", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Description");
    expect(container.textContent).toContain("Security");
    expect(container.textContent).toContain("Versioning");
    expect(container.textContent).toContain("Publisher Trust");
  });

  it("renders breakdown details", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("220 chars");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("tests=✓");
  });

  it("renders weight percentages", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("25%"); // security weight
    expect(container.textContent).toContain("15%"); // description weight
  });

  it("calls onApprove", () => {
    const onApprove = vi.fn();
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={onApprove}
        onReject={vi.fn()}
      />,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Approve")!,
    );
    expect(onApprove).toHaveBeenCalledOnce();
  });

  it("calls onReject", () => {
    const onReject = vi.fn();
    const { container } = render(
      <AppReviewScoreCard
        score={GOOD_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={onReject}
      />,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Reject")!,
    );
    expect(onReject).toHaveBeenCalledOnce();
  });

  it("renders poor grade", () => {
    const { container } = render(
      <AppReviewScoreCard
        score={POOR_SCORE}
        appName="App"
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Poor");
    expect(container.textContent).toContain("28");
  });
});
