import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SupportFaqAccordion } from "@/components/support-faq-accordion";

describe("SupportFaqAccordion", () => {
  const items = [
    { id: "1", question: "How to publish?", answer: "Submit for review.", category: "publishing" },
    { id: "2", question: "What are webhooks?", answer: "HTTP callbacks.", category: "technical" },
  ];
  it("renders questions", () => {
    const { container } = render(<SupportFaqAccordion items={items} />);
    expect(container.textContent).toContain("How to publish?");
    expect(container.textContent).toContain("What are webhooks?");
  });
  it("expands on click", () => {
    const { container } = render(<SupportFaqAccordion items={items} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(container.textContent).toContain("Submit for review.");
  });
});
