import React, { useState } from 'react';
import { Card, Pill, SectionTitle } from '../ui';

interface AssistantEntry {
  formal: string;
  short: string;
  handle: string;
  responsibility: string;
  link: string;
}

const ASSISTANTS: AssistantEntry[] = [
  { formal: 'Theodore', short: 'Theo', handle: '@theobiblebot', responsibility: 'Scripture, devotionals, saved verses, and theological assistance', link: 'https://t.me/theobiblebot' },
  { formal: 'Lucy', short: 'Lusie', handle: '@lusiequizbot', responsibility: 'Bible quizzes, XP, competitions, and leaderboards', link: 'https://t.me/lusiequizbot' },
  { formal: 'Edmund', short: 'Edie', handle: '@ediecalendarbot', responsibility: 'Calendar, events, meetings, birthdays, and reminders', link: 'https://t.me/ediecalendarbot' },
  { formal: 'Peter', short: 'Pete', handle: '@petemodbot', responsibility: 'Moderation, anti-spam, and community safety', link: 'https://t.me/petemodbot' },
  { formal: 'Susan', short: 'Susie', handle: '@susiehelpsbot', responsibility: 'Onboarding, welcome, and hospitality', link: 'https://t.me/susiehelpsbot' },
];

const COMMUNITY_SPACES = [
  { name: 'Telegram Community', role: 'Main fellowship group — general fellowship, announcements, and support', link: 'https://t.me/youthopiabiblecommunity' },
  { name: 'WhatsApp Community', role: 'Daily encouragement and conversation on WhatsApp', link: 'https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn' },
  { name: 'Facebook Community', role: 'Fellowship and community updates on Facebook', link: 'https://www.facebook.com/share/g/18wG8aWB6t/' },
];

const FAQS = [
  {
    question: 'What is YouThopia Bible Community?',
    answer: 'YouThopia Bible Community is a digital fellowship of believers dedicated to studying Scripture, deepening faith, playing and learning together, and sharing God\'s love all the way.',
  },
  {
    question: 'What is YouThopiaOS?',
    answer: 'YouThopiaOS is the software engine powering our five Telegram assistants (Theodore, Lucy, Edmund, Peter, Susan) and this unified Mini App.',
  },
  {
    question: 'How do I earn XP and level up?',
    answer: 'You earn YouTopian Points by taking quizzes with Lusie and completing Scripture challenges. Your XP follows you across every part of the community.',
  },
  {
    question: 'How does verification work?',
    answer: 'When you open the Mini App inside Telegram, your signed Telegram identity is verified server-side before your profile is shown.',
  },
  {
    question: 'What is the Trust Score?',
    answer: 'Peter maintains a Trust Score out of 100 for every member, based on verification, clean interactions, and account standing.',
  },
];

const ONBOARDING = [
  { step: '01', title: 'Set Bible preferences', description: 'Choose your default Scripture translation in Word.' },
  { step: '02', title: 'Earn community XP', description: 'Take a quiz in Play to build your member rank.' },
  { step: '03', title: 'Join a gathering', description: 'RSVP for weekly studies and prayer calls in Gather.' },
];

interface CommunityTabProps {
  /** Opens the full-screen guided YouThopia Tour overlay (rendered by App). */
  onOpenTour?: () => void;
}

export const CommunityTab: React.FC<CommunityTabProps> = ({ onOpenTour }) => {
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  return (
    <div className="section-stack">
      <section className="page-heading">
        <span className="quiet-chip">Community guide</span>
        <h1>Your YouThopia Handbook.</h1>
        <p>Find the assistants, manage your settings, and learn how everything fits together.</p>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Start here" right={<Pill color="purple">5 pages</Pill>}>The YouThopia Tour</SectionTitle>
        <Card style={{ padding: 16 }}>
          <p className="muted-copy" style={{ margin: 0 }}>
            New here? Take the guided tour of our mission, vision, the five pillars, and how your journey ranks up in YP.
            Finishing it marks you oriented and claims your one-time welcome boost.
          </p>
          <button className="primary-button" onClick={onOpenTour} style={{ marginTop: 12, width: '100%' }}>
            🧭 Take the tour
          </button>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Manage" right={<Pill color="slate">In app</Pill>}>Your account</SectionTitle>
        <Card style={{ padding: 16 }}>
          <div style={{ display: 'grid', gap: 12 }}>
            <div>
              <strong style={{ fontSize: 14 }}>Profile</strong>
              <p className="muted-copy" style={{ marginTop: 4 }}>
                Open your growth passport from the avatar button at the top to review rank, XP, accuracy, and trust.
              </p>
            </div>
            <div>
              <strong style={{ fontSize: 14 }}>Preferences</strong>
              <p className="muted-copy" style={{ marginTop: 4 }}>
                Your Bible translation lives in Word, and daily devotional delivery follows the same setting.
              </p>
            </div>
          </div>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Safety" right={<Pill color="success">Shielded</Pill>}>Peter, our guardian</SectionTitle>
        <Card style={{ padding: 16 }}>
          <p className="muted-copy" style={{ margin: 0 }}>
            Peter quietly protects the community from spam and unauthorized bots. Your account passes verification with an optimal{' '}
            <strong style={{ color: 'var(--success)' }}>100/100 Trust Score</strong> based on clean interactions and good standing.
          </p>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Assistants" right={<Pill color="purple">5 active</Pill>}>Meet the team</SectionTitle>
        <div style={{ display: 'grid', gap: 10 }}>
          {ASSISTANTS.map((a) => (
            <Card key={a.handle} hover style={{ padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <strong style={{ fontSize: 14 }}>{a.formal} <span style={{ color: 'var(--text-muted)', fontWeight: 650 }}>({a.short})</span></strong>
                  <p className="muted-copy" style={{ marginTop: 4 }}>{a.responsibility}</p>
                  <span style={{ display: 'inline-block', marginTop: 8, color: 'var(--primary-purple)', fontSize: 11, fontWeight: 750 }}>{a.handle}</span>
                </div>
                <a className="secondary-button" href={a.link} target="_blank" rel="noreferrer" style={{ minHeight: 36, paddingInline: 13 }}>Open</a>
              </div>
            </Card>
          ))}
        </div>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Learn the flow" right={<Pill color="purple">3 steps</Pill>}>Getting started</SectionTitle>
        <Card style={{ padding: 16 }}>
          <div style={{ display: 'grid', gap: 12 }}>
            {ONBOARDING.map((s) => (
              <div key={s.step} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 800,
                    color: 'var(--primary-purple)',
                    background: 'var(--purple-50)',
                    border: '1px solid var(--purple-100)',
                    padding: '5px 9px',
                    borderRadius: 'var(--radius-md)',
                    flexShrink: 0,
                  }}
                >
                  {s.step}
                </span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700 }}>{s.title}</div>
                  <p className="muted-copy" style={{ marginTop: 2 }}>{s.description}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Questions">Community FAQ</SectionTitle>
        <Card style={{ padding: 18 }}>
          <div style={{ display: 'grid', gap: 8 }}>
            {FAQS.map((faq, index) => {
              const isOpen = activeFaq === index;
              return (
                <div key={index} style={{ borderBottom: index < FAQS.length - 1 ? '1px solid var(--slate-100)' : undefined, paddingBottom: 8 }}>
                  <button
                    onClick={() => setActiveFaq(isOpen ? null : index)}
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      background: 'none',
                      border: 0,
                      padding: '8px 0',
                      fontSize: 13,
                      fontWeight: 700,
                      color: 'var(--ink)',
                      cursor: 'pointer',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      gap: 12,
                    }}
                  >
                    <span>{faq.question}</span>
                    <span style={{ color: isOpen ? 'var(--primary-purple)' : 'var(--text-muted)', fontSize: 18, fontWeight: 700, flexShrink: 0 }}>
                      {isOpen ? '−' : '+'}
                    </span>
                  </button>
                  <div style={{ maxHeight: isOpen ? 220 : 0, overflow: 'hidden', transition: 'max-height 0.25s var(--ease)' }}>
                    <p className="muted-copy" style={{ margin: '2px 0 6px 0' }}>{faq.answer}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Say hello">Community places</SectionTitle>
        {COMMUNITY_SPACES.map((space) => (
          <a key={space.name} className="feature-row" href={space.link} target="_blank" rel="noreferrer">
            <span style={{ minWidth: 0 }}>
              <strong>{space.name}</strong>
              <span>{space.role}</span>
            </span>
            <span className="feature-row-arrow">→</span>
          </a>
        ))}
      </section>
    </div>
  );
};
