import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenInfoCard } from "@/components/token-info-card";

describe("TokenInfoCard", () => {
  it("shows active", () => {
    const { container } = render(<TokenInfoCard active={true} scope="read:cohorts" clientId="osk_abc" />);
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("🟢");
  });
  it("shows inactive", () => {
    const { container } = render(<TokenInfoCard active={false} />);
    expect(container.textContent).toContain("Inactive");
    expect(container.textContent).toContain("🔴");
  });
  it("shows scope", () => {
    const { container } = render(<TokenInfoCard active={true} scope="read:cohorts write:projects" />);
    expect(container.textContent).toContain("read:cohorts");
  });
  it("shows client id", () => {
    const { container } = render(<TokenInfoCard active={true} clientId="osk_test123" />);
    expect(container.textContent).toContain("osk_test123");
  });
});
