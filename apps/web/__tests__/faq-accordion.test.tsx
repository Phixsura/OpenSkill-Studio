import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FaqAccordion } from "@/components/faq-accordion";

describe("FaqAccordion", () => {
  it("renders and expands", () => {
    const { container, getByText } = render(
      <FaqAccordion items={[
        { id: "q1", question: "How do I get an API key?", answer: "Go to Settings", category: "api" },
        { id: "q2", question: "Rate limits?", answer: "1000/min", category: "api" },
      ]} />
    );
    expect(container.textContent).toContain("How do I get an API key?");
    expect(container.textContent).not.toContain("Go to Settings");
    fireEvent.click(getByText("How do I get an API key?"));
    expect(container.textContent).toContain("Go to Settings");
  });
});
