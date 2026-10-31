import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DevPortalCard from "../src/components/api-developer-platform-sdk-consumer-api-dev-portal-card";

describe("DevPortalCard", () => {
  it("renders title and steps", () => {
    const { container } = render(<DevPortalCard />);
    expect(container.textContent).toContain("Developer Portal");
    expect(container.textContent).toContain("Create Account");
    expect(container.textContent).toContain("Make First Call");
  });

  it("shows quicklinks and section count", () => {
    const { container } = render(<DevPortalCard />);
    expect(container.textContent).toContain("API Docs");
    expect(container.textContent).toContain("24 documentation sections");
  });
});
