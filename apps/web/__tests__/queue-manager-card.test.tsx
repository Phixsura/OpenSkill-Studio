import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import QueueManagerCard from "../src/components/queue-manager-card";

const emailQueue = {
  queue_name: "emails",
  pending: 42,
  processing: 3,
  completed: 1500,
  failed: 5,
  dead_letter: 2,
};

const webhookQueue = {
  queue_name: "webhooks",
  pending: 0,
  processing: 0,
  completed: 500,
  failed: 0,
  dead_letter: 0,
};

describe("QueueManagerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<QueueManagerCard queues={[emailQueue]} appName="My App" />);
    expect(container.textContent).toContain("Job Queues");
    expect(container.textContent).toContain("My App");
  });

  it("shows pending count badge", () => {
    const { container } = render(<QueueManagerCard queues={[emailQueue]} appName="App" />);
    expect(container.textContent).toContain("42 pending");
  });

  it("shows dead-letter badge", () => {
    const { container } = render(<QueueManagerCard queues={[emailQueue]} appName="App" />);
    expect(container.textContent).toContain("2 dead-letter");
  });

  it("renders queue name", () => {
    const { container } = render(<QueueManagerCard queues={[emailQueue]} appName="App" />);
    expect(container.textContent).toContain("emails");
  });

  it("shows processed count", () => {
    const { container } = render(<QueueManagerCard queues={[emailQueue]} appName="App" />);
    expect(container.textContent).toContain("1.5K processed");
  });

  it("shows status dots", () => {
    const { container } = render(<QueueManagerCard queues={[emailQueue]} appName="App" />);
    expect(container.textContent).toContain("42 pending");
    expect(container.textContent).toContain("3 active");
    expect(container.textContent).toContain("5 failed");
    expect(container.textContent).toContain("2 dead");
  });

  it("hides zero-count statuses", () => {
    const { container } = render(<QueueManagerCard queues={[webhookQueue]} appName="App" />);
    expect(container.textContent).not.toContain("pending");
    expect(container.textContent).not.toContain("dead");
  });

  it("shows empty state", () => {
    const { container } = render(<QueueManagerCard queues={[]} appName="App" />);
    expect(container.textContent).toContain("No queues");
  });
});
