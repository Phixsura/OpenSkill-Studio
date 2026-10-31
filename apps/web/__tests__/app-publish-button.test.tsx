import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppPublishButton } from "@/components/app-publish-button";

describe("AppPublishButton", () => {
  it("shows publish for approved", () => {
    const { container } = render(<AppPublishButton appStatus="approved" onPublish={vi.fn()} />);
    expect(container.textContent).toContain("Publish");
  });

  it("disabled for draft", () => {
    const { container } = render(<AppPublishButton appStatus="draft" onPublish={vi.fn()} />);
    expect(container.textContent).toContain("Cannot Publish");
  });

  it("shows already published", () => {
    const { container } = render(<AppPublishButton appStatus="published" onPublish={vi.fn()} />);
    expect(container.textContent).toContain("Already Published");
  });

  it("shows awaiting review", () => {
    const { container } = render(<AppPublishButton appStatus="submitted" onPublish={vi.fn()} />);
    expect(container.textContent).toContain("Awaiting Review");
  });
});
