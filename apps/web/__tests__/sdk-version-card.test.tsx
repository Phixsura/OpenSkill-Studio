import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SDKVersionCard from "../src/components/sdk-version-card";

const versions = [
  { version: "2.0.0", requests: 5000, consumers: 20, latest: true },
  { version: "1.5.0", requests: 1000, consumers: 5, latest: false },
  { version: "1.0.0", requests: 100, consumers: 1, latest: false },
];

describe("SDKVersionCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <SDKVersionCard versions={versions} outdatedCount={6} appName="App" />,
    );
    expect(container.textContent).toContain("SDK Versions");
    expect(container.textContent).toContain("3 versions");
    expect(container.textContent).toContain("6 outdated");
  });

  it("shows version numbers with latest badge", () => {
    const { container } = render(
      <SDKVersionCard versions={versions} outdatedCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("latest");
    expect(container.textContent).toContain("1.5.0");
  });

  it("shows consumer and request counts", () => {
    const { container } = render(
      <SDKVersionCard versions={versions} outdatedCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("20 consumers");
    expect(container.textContent).toContain("5000 reqs");
  });

  it("shows empty state", () => {
    const { container } = render(<SDKVersionCard versions={[]} outdatedCount={0} appName="App" />);
    expect(container.textContent).toContain("No SDK usage tracked");
  });
});
