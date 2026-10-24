import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContactPageLayout } from "@/components/contact-page-layout";

describe("ContactPageLayout", () => {
  it("renders", () => {
    const channels = [{ id: "email", label: "Email", icon: "📧", description: "24h response", url: "#" }];
    const { container } = render(<ContactPageLayout channels={channels} onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Get in Touch");
    expect(container.textContent).toContain("Email");
    expect(container.textContent).toContain("Send a Message");
    expect(container.textContent).toContain("Send Message");
  });
});
