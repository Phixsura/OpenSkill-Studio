import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublishFlow } from "@/components/publish-flow";

describe("PublishFlow", () => {
  const checks = [
    { check: "manifest_valid", label: "Manifest Valid", pass: true },
    { check: "tests_passing", label: "Tests Passing", pass: false },
  ];
  it("renders publish flow", () => {
    const { container } = render(
      <PublishFlow checks={checks} canPublish={false} score={50} version="2.0.0" onPublish={vi.fn()} />
    );
    expect(container.textContent).toContain("Publish v2.0.0");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Manifest Valid");
    expect(container.textContent).toContain("Complete all checks");
  });
});
