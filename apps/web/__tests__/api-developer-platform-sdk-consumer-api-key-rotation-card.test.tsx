import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import KeyRotationCard from "../src/components/api-developer-platform-sdk-consumer-api-key-rotation-card";

describe("KeyRotationCard", () => {
  it("renders title and keys", () => {
    const { container } = render(<KeyRotationCard />);
    expect(container.textContent).toContain("Key Rotation");
    expect(container.textContent).toContain("key_a1b2c3");
    expect(container.textContent).toContain("key_d4e5f6");
  });

  it("shows active count", () => {
    const { container } = render(<KeyRotationCard />);
    expect(container.textContent).toContain("2 active keys");
    expect(container.textContent).toContain("auto");
  });
});
