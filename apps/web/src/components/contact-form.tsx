"use client";

import { useState } from "react";

interface ContactFormProps { topics: { id: string; label: string }[];
  onSubmit: (data: { name: string; email: string; topic: string; message: string }) => void; }

export function ContactForm({ topics, onSubmit }: ContactFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [topic, setTopic] = useState(topics[0]?.id ?? "");
  const [message, setMessage] = useState("");

  return (
    <div className="mx-auto max-w-md space-y-4">
      <h2 className="text-lg font-bold">Contact Us</h2>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Name</label>
        <input value={name} onChange={e => setName(e.target.value)}
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Email</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)}
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Topic</label>
        <select value={topic} onChange={e => setTopic(e.target.value)}
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600">
          {topics.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
        </select>
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Message</label>
        <textarea value={message} onChange={e => setMessage(e.target.value)} rows={4}
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <button onClick={() => onSubmit({ name, email, topic, message })}
        className="w-full rounded bg-blue-600 py-2 text-sm text-white">Send Message</button>
    </div>
  );
}
