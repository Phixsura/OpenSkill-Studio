import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeedbackSummaryCard } from "@/components/feedback-summary-card";

const MOCK_SUMMARY = {
  app_id: "app-1",
  total_count: 42,
  avg_rating: 4.2,
  distribution: { 1: 2, 2: 3, 3: 5, 4: 12, 5: 20 },
  sentiment_breakdown: { positive: 32, neutral: 5, negative: 5 },
  recent: [
    {
      feedback_id: "fb-1",
      user_id: "user-a",
      rating: 5,
      comment: "Amazing app!",
      sentiment: "positive" as const,
      created_at: "2026-10-28T10:00:00Z",
    },
    {
      feedback_id: "fb-2",
      user_id: "user-b",
      rating: 2,
      comment: "Needs work",
      sentiment: "negative" as const,
      created_at: "2026-10-28T09:00:00Z",
    },
  ],
};

const EMPTY = {
  ...MOCK_SUMMARY,
  total_count: 0,
  avg_rating: 0,
  distribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
  sentiment_breakdown: {},
  recent: [],
};

describe("FeedbackSummaryCard", () => {
  it("renders heading and app name", () => {
    const { container } = render(<FeedbackSummaryCard summary={MOCK_SUMMARY} appName="My App" />);
    expect(container.textContent).toContain("User Feedback");
    expect(container.textContent).toContain("My App");
  });

  it("renders review count", () => {
    const { container } = render(<FeedbackSummaryCard summary={MOCK_SUMMARY} appName="App" />);
    expect(container.textContent).toContain("42 reviews");
  });

  it("renders average rating", () => {
    const { container } = render(<FeedbackSummaryCard summary={MOCK_SUMMARY} appName="App" />);
    expect(container.textContent).toContain("4.2");
  });

  it("renders star display", () => {
    const { container } = render(<FeedbackSummaryCard summary={MOCK_SUMMARY} appName="App" />);
    expect(container.textContent).toContain("★");
  });

  it("renders distribution bars", () => {
    const { container } = render(<FeedbackSummaryCard summary={MOCK_SUMMARY} appName="App" />);
    expect(container.textContent).toContain("20"); // 5-star count
    expect(container.textContent).toContain("12"); // 4-star count
  });

  it("renders sentiment breakdown", () => {
    const { container } = render(<FeedbackSummaryCard summary={MOCK_SUMMARY} appName="App" />);
    expect(container.textContent).toContain("32 Positive");
    expect(container.textContent).toContain("5 Negative");
  });

  it("renders recent feedback", () => {
    const { container } = render(<FeedbackSummaryCard summary={MOCK_SUMMARY} appName="App" />);
    expect(container.textContent).toContain("Recent");
    expect(container.textContent).toContain("Amazing app!");
    expect(container.textContent).toContain("Needs work");
  });

  it("renders user ids", () => {
    const { container } = render(<FeedbackSummaryCard summary={MOCK_SUMMARY} appName="App" />);
    expect(container.textContent).toContain("user-a");
    expect(container.textContent).toContain("user-b");
  });

  it("shows empty state", () => {
    const { container } = render(<FeedbackSummaryCard summary={EMPTY} appName="App" />);
    expect(container.textContent).toContain("No feedback yet");
  });
});
