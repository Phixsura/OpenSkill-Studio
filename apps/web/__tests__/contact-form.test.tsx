import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContactForm } from "@/components/contact-form";

describe("ContactForm", () => {
  it("renders form", () => {
    const onSubmit = vi.fn();
    const { container, getByText } = render(
      <ContactForm topics={["general", "support"]} onSubmit={onSubmit} confirmation={null} />
    );
    expect(container.textContent).toContain("Contact Us");
    fireEvent.click(getByText("Send Message"));
    expect(onSubmit).toHaveBeenCalled();
  });

  it("renders confirmation", () => {
    const { container } = render(
      <ContactForm topics={["general"]} onSubmit={vi.fn()} confirmation="Thanks! We'll respond soon." />
    );
    expect(container.textContent).toContain("Thanks!");
  });
});
