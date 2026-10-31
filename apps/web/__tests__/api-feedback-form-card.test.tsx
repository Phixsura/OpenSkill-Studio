import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIFeedbackFormCard from "../src/components/api-feedback-form-card";

describe("APIFeedbackFormCard", () => {
  it("renders header and metrics", () => {
    const { container } = render(<APIFeedbackFormCard avgRating={4.2} nps={60} totalCount={50} categories={{ api: 30, docs: 20 }} appName="App" />);
    expect(container.textContent).toContain("Developer Feedback");
    expect(container.textContent).toContain("4.2");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("50 responses");
  });

  it("shows categories", () => {
    const { container } = render(<APIFeedbackFormCard avgRating={4} nps={50} totalCount={10} categories={{ api: 7, docs: 3 }} appName="App" />);
    expect(container.textContent).toContain("api: 7");
    expect(container.textContent).toContain("docs: 3");
  });
});
