import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContactForm } from "@/components/contact-form";

describe("ContactForm", () => {
  const topics = [{ id: "general", label: "General" }, { id: "technical", label: "Technical" }];
  it("renders form", () => {
    const { container } = render(<ContactForm topics={topics} onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Contact Us");
    expect(container.textContent).toContain("Send Message");
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.querySelector("textarea")).toBeTruthy();
  });
});
