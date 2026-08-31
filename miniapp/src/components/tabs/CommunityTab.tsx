import React, { useState } from 'react';
import { Card, Pill, SectionTitle } from '../ui';

export const CommunityTab: React.FC = () => {
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  const directoryChannels = [
    {
      name: 'Main Community Group',
      role: 'General Fellowship & Announcements',
      tag: 'Primary Group',
    },
    {
      name: 'Scripture & Devotional Channel',
      role: 'Daily VOTD & Reflection Studies',
      tag: 'Theo Bot',
    },
    {
      name: 'Prayer & Intercession Line',
      role: 'Prayer Requests & Midweek Sessions',
      tag: 'Eddy Bot',
    },
    {
      name: 'Quiz & Challenge Arena',
      role: 'Daily Bible Trivia & Leaderboards',
      tag: 'Lusy Bot',
    },
    {
      name: 'Security & Moderation Checkpoint',
      role: 'Captcha Verification & Trust Ratings',
      tag: 'Pete Bot',
    },
  ];

  const onboardingSteps = [
    {
      step: '01',
      title: 'Set Bible Preferences',
      description: 'Choose your default Scripture translation (KJV, ASV, WEB, BBE) in the Bible tab.',
    },
    {
      step: '02',
      title: 'Earn Community XP',
      description: 'Participate in daily quizzes and challenges to build your member rank.',
    },
    {
      step: '03',
      title: 'Join Community Events',
      description: 'RSVP for weekly Bible studies and midweek prayer calls in the Events tab.',
    },
  ];

  const faqs = [
    {
      question: 'What is YouThopia Bible Community?',
      answer:
        'YouThopia Bible Community is a vibrant digital fellowship of believers dedicated to studying sacred Scripture, deepening faith, participating in daily interactive quizzes, and sharing God\'s love all the way.',
    },
    {
      question: 'What is YouThopiaOS?',
      answer:
        'YouThopiaOS is the underlying software engine powering our 5 specialized Telegram assistants (Theo, Lusy, Pete, Eddy, Susy) and this unified Mini App platform.',
    },
    {
      question: 'How do I earn XP and level up?',
      answer: 'You earn YouTopian Points (XP) by participating in daily quizzes hosted by Lusy Bot and completing Scripture challenges.',
    },
    {
      question: 'How does verification work?',
      answer: 'When you open the Mini App inside Telegram, your cryptographic initData signature is verified server-side by our FastAPI gateway.',
    },
    {
      question: 'What is Pete Bot\'s Trust Score?',
      answer:
        'Pete Bot calculates a Trust Score (100/100) for every member based on captcha verification, clean group interactions, and account standing.',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-color)', letterSpacing: '-0.02em' }}>
          Community & Hospitality Hub
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
          Powered by Susy & Pete Bots &bull; Directory, Hospitality & Security
        </p>
      </div>

      {/* Susy Host Welcome Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg,#f5f3ff,#ede9fe)',
          borderRadius: 'var(--radius-lg)',
          padding: 18,
          border: '1px solid var(--purple-100)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: -30,
            right: -20,
            width: 90,
            height: 90,
            borderRadius: '50%',
            background: 'rgba(109,40,217,0.08)',
          }}
        />
        <div style={{ position: 'relative' }}>
          <Pill color="purple" style={{ marginBottom: 8 }}>
            Hospitality & Onboarding Host
          </Pill>
          <p style={{ fontSize: 14, color: 'var(--slate-700)', lineHeight: 1.65, margin: 0 }}>
            Welcome to the YouThopia Bible Community directory. I am Susy, your hostess and onboarding guide. Use this space to explore our
            channels, understand community rules, and learn how to participate.
          </p>
        </div>
      </div>

      {/* Pete Security Checkpoint Card */}
      <Card style={{ padding: 18 }} hover>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              color: 'var(--success)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            Pete Security & Trust Checkpoint
          </span>
          <Pill color="success">● Account Shielded</Pill>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
          Pete Bot actively guards our community against spam and unauthorized bots. Your account has passed verification with a{' '}
          <strong style={{ color: 'var(--success)' }}>100/100 Trust Score</strong>.
        </p>
      </Card>

      {/* Directory Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <SectionTitle>Community Directory (5 Assistants)</SectionTitle>

        {directoryChannels.map((chan, idx) => (
          <Card key={idx} hover style={{ padding: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-color)' }}>{chan.name}</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{chan.role}</div>
            </div>
            <Pill color="purple">{chan.tag}</Pill>
          </Card>
        ))}
      </div>

      {/* 3-Step Onboarding Guide */}
      <Card style={{ padding: 18 }} hover>
        <SectionTitle
          right={<Pill color="purple">3 Steps</Pill>}
        >
          Member Onboarding Guide
        </SectionTitle>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {onboardingSteps.map((s) => (
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
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-color)' }}>{s.title}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2, lineHeight: 1.5 }}>{s.description}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Community FAQ */}
      <Card style={{ padding: 18 }} hover>
        <SectionTitle>Frequently Asked Questions</SectionTitle>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {faqs.map((faq, index) => {
            const isOpen = activeFaq === index;
            return (
              <div key={index} style={{ borderBottom: '1px solid var(--slate-100)', paddingBottom: 8 }}>
                <button
                  onClick={() => setActiveFaq(isOpen ? null : index)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    background: 'none',
                    border: 'none',
                    padding: '8px 0',
                    fontSize: 13,
                    fontWeight: 600,
                    color: 'var(--text-color)',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span>{faq.question}</span>
                  <span
                    style={{
                      color: isOpen ? 'var(--primary-purple)' : 'var(--text-muted)',
                      fontSize: 18,
                      fontWeight: 700,
                      flexShrink: 0,
                      marginLeft: 12,
                      transition: 'color 0.15s var(--ease)',
                    }}
                  >
                    {isOpen ? '−' : '+'}
                  </span>
                </button>
                <div
                  style={{
                    maxHeight: isOpen ? 200 : 0,
                    overflow: 'hidden',
                    transition: 'max-height 0.25s var(--ease)',
                  }}
                >
                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, margin: '2px 0 6px 0' }}>{faq.answer}</p>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};
