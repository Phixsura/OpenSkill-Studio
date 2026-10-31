"use client";
import { useState } from "react";

interface ContactFormProps { topics: string[];
  onSubmit: (data: { name: string; email: string; topic: string; message: string }) => void;
  confirmation: string | null; }

export function ContactForm({ topics, onSubmit, confirmation }: ContactFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [topic, setTopic] = useState(topics[0] || "general");
  const [message, setMessage] = useState("");
  return (
    <div className="rounded-xl border p-6 dark:border-gray-700 max-w-lg">
      <h3 className="text-lg font-bold mb-4">📬 Contact Us</h3>
      {confirmation ? (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg text-sm text-green-700">{confirmation}</div>
      ) : (
        <div className="space-y-3">
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Name"
            className="w-full text-sm px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-600" />
          <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" type="email"
            className="w-full text-sm px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-600" />
          <select value={topic} onChange={e => setTopic(e.target.value)}
            className="w-full text-sm px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-600">
            {topics.map(t => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
          </select>
          <textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="Your message..."
            rows={4} className="w-full text-sm px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={() => onSubmit({ name, email, topic, message })}
            className="w-full py-2.5 bg-blue-600 text-white text-sm rounded-lg font-medium hover:bg-blue-700">Send Message</button>
        </div>
      )}
    </div>
  );
}
