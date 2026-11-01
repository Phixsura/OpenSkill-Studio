import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIKeyRotationCard from "../src/components/api-key-rotation-card";

const keys = [
  {
    key_id: "k1",
    prefix: "abc12345",
    label: "Production",
    is_active: true,
    revoked: false,
    is_expired: false,
    created_at: 1000,
  },
  {
    key_id: "k2",
    prefix: "xyz98765",
    label: "Staging",
    is_active: false,
    revoked: true,
    is_expired: false,
    created_at: 900,
  },
  {
    key_id: "k3",
    prefix: "def55555",
    label: "",
    is_active: false,
    revoked: false,
    is_expired: true,
    created_at: 800,
  },
];

describe("APIKeyRotationCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIKeyRotationCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("API Key Rotation");
    expect(container.textContent).toContain("1 active / 3 total");
  });

  it("shows key prefixes", () => {
    const { container } = render(<APIKeyRotationCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("abc12345...");
    expect(container.textContent).toContain("xyz98765...");
  });

  it("shows labels", () => {
    const { container } = render(<APIKeyRotationCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("Staging");
  });

  it("shows status badges", () => {
    const { container } = render(<APIKeyRotationCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("revoked");
    expect(container.textContent).toContain("expired");
  });

  it("shows empty state", () => {
    const { container } = render(<APIKeyRotationCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No API keys");
  });
});
