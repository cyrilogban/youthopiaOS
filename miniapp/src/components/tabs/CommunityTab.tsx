import React, { useState } from 'react';

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
      answer: 'YouThopia Bible Community is a vibrant digital fellowship of believers dedicated to studying sacred Scripture, deepening faith, participating in daily interactive quizzes, and sharing God\'s love all the way.',
    },
    {
      question: 'What is YouThopiaOS?',
      answer: 'YouThopiaOS is the underlying software engine powering our 5 specialized Telegram assistants (Theo, Lusy, Pete, Eddy, Susy) and this unified Mini App platform.',
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
      answer: 'Pete Bot calculates a Trust Score (100/100) for every member based on captcha verification, clean group interactions, and account standing.',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 4px 0', color: '#0f172a' }}>
          Community & Hospitality Hub
        </h2>
        <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>
          Powered by Susy & Pete Bots &bull; Directory, Hospitality & Security
        </p>
      </div>

      {/* Susy Host Welcome Banner */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '14px',
          padding: '18px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#6d28d9', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Hospitality & Onboarding Host
          </span>
        </div>
        <p style={{ fontSize: '14px', color: '#334155', lineHeight: '1.6', margin: 0 }}>
          Welcome to the YouThopia Bible Community directory. I am Susy, your hostess and onboarding guide. Use this space to explore our channels, understand community rules, and learn how to participate.
        </p>
      </div>

      {/* Pete Security Checkpoint Card */}
      <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '14px', padding: '18px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#16a34a', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Pete Security & Trust Checkpoint
          </span>
          <span style={{ fontSize: '11px', color: '#15803d', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>
            ● Account Shielded
          </span>
        </div>
        <p style={{ fontSize: '13px', color: '#475569', lineHeight: '1.5', margin: 0 }}>
          Pete Bot actively guards our community against spam and unauthorized bots. Your account has passed verification with a <strong>100/100 Trust Score</strong>.
        </p>
      </div>

      {/* Directory Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0, color: '#0f172a' }}>
          Community Directory (5 Assistants)
        </h3>

        {directoryChannels.map((chan, idx) => (
          <div
            key={idx}
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '14px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>{chan.name}</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>{chan.role}</div>
            </div>
            <span style={{ fontSize: '11px', color: '#6d28d9', backgroundColor: '#f5f3ff', border: '1px solid #ddd6fe', padding: '3px 8px', borderRadius: '4px', fontWeight: 600 }}>
              {chan.tag}
            </span>
          </div>
        ))}
      </div>

      {/* 3-Step Onboarding Guide */}
      <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '14px', padding: '18px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 700, margin: '0 0 14px 0', color: '#0f172a' }}>
          Member Onboarding Guide
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {onboardingSteps.map((s) => (
            <div key={s.step} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
              <span style={{ fontSize: '12px', fontWeight: 800, color: '#6d28d9', backgroundColor: '#f1f5f9', padding: '4px 8px', borderRadius: '6px' }}>
                {s.step}
              </span>
              <div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{s.title}</div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px', lineHeight: '1.5' }}>{s.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Community FAQ */}
      <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '14px', padding: '18px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 700, margin: '0 0 12px 0', color: '#0f172a' }}>
          Frequently Asked Questions
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {faqs.map((faq, index) => {
            const isOpen = activeFaq === index;
            return (
              <div key={index} style={{ borderBottom: '1px solid #f1f5f9', paddingBottom: '8px' }}>
                <button
                  onClick={() => setActiveFaq(isOpen ? null : index)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    background: 'none',
                    border: 'none',
                    padding: '6px 0',
                    fontSize: '13px',
                    fontWeight: 600,
                    color: '#0f172a',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span>{faq.question}</span>
                  <span style={{ color: '#64748b', fontSize: '16px' }}>{isOpen ? '-' : '+'}</span>
                </button>
                {isOpen && (
                  <p style={{ fontSize: '12px', color: '#475569', lineHeight: '1.6', margin: '4px 0 6px 0' }}>
                    {faq.answer}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
