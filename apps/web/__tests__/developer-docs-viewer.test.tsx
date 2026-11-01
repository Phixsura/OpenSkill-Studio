import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperDocsViewer } from "@/components/developer-docs-viewer";

const mockPages = [
  { id: "1", title: "Getting Started", slug: "getting-started", category: "Guide", content: "Welcome to the SDK. Here is how to get started with your first extension." },
  { id: "2", title: "Authentication", slug: "auth", category: "Guide", content: "Use OAuth 2.0 to authenticate. Register your app and get credentials." },
  { id: "3", title: "Webhooks API", slug: "webhooks", category: "API Reference", content: "POST /webhooks to create a subscription. Include event types in the body." },
  { id: "4", title: "Rate Limits", slug: "rate-limits", category: "API Reference", content: "Default rate limit is 100 requests per minute per API key." },
];

describe("DeveloperDocsViewer", () => {
  it("renders sidebar with categories", () => {
    const { container } = render(<DeveloperDocsViewer pages={mockPages} />);
    expect(container.textContent).toContain("Guide");
    expect(container.textContent).toContain("API Reference");
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Webhooks API");
  });

  it("shows first page content by default", () => {
    const { container } = render(<DeveloperDocsViewer pages={mockPages} />);
    expect(container.textContent).toContain("Welcome to the SDK");
  });

  it("navigates to selected page", () => {
    const { container, getByText } = render(<DeveloperDocsViewer pages={mockPages} />);
    fireEvent.click(getByText("Rate Limits"));
    expect(container.textContent).toContain("100 requests per minute");
  });

  it("filters pages by search", () => {
    const { container, getByPlaceholderText } = render(<DeveloperDocsViewer pages={mockPages} />);
    fireEvent.change(getByPlaceholderText("Search docs..."), { target: { value: "webhook" } });
    expect(container.textContent).toContain("Webhooks API");
    expect(container.textContent).not.toContain("Rate Limits");
  });
});
