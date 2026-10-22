import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SecretsManagement } from "@/components/secrets-management";

describe("SecretsManagement", () => {
  it("shows secrets", () => {
    const { container } = render(<SecretsManagement secrets={[{ key: "API_KEY" }]} canAdd={true} remaining={19} onAdd={vi.fn()} />);
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("19 remaining");
  });
  it("empty state", () => {
    const { container } = render(<SecretsManagement secrets={[]} canAdd={true} remaining={20} />);
    expect(container.textContent).toContain("No secrets");
  });
});
