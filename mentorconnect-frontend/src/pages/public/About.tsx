export default function About() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 py-16">
      <p className="font-mono text-sm text-accent">about us</p>
      <h1 className="mt-2 font-display text-3xl sm:text-4xl font-semibold text-ink-800 dark:text-ink-50">
        Guidance shouldn't be a gamble.
      </h1>
      <div className="mt-6 space-y-4 text-ink-600 dark:text-ink-300 leading-relaxed">
        <p>
          MentorConnect was built on a simple idea: the right conversation at the right time can change the
          direction of someone's career. We connect students with mentors who have already navigated the
          path they're on — not through cold outreach, but through a platform built for real, ongoing
          relationships.
        </p>
        <p>
          Every mentor on our platform goes through document verification and admin approval before they can
          accept students. That means when you book a session, you're talking to someone whose credentials
          have actually been checked.
        </p>
        <p>
          Whether you're looking for career advice, technical mentorship, or someone to help you think through
          your next big decision, MentorConnect gives you the tools to find them, message them, and book time
          together — all in one place.
        </p>
      </div>
    </div>
  );
}