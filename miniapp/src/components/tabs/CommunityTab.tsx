import React, { useState } from 'react';
import { Card, Pill, SectionTitle } from '../ui';

export const CommunityTab: React.FC = () => {
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  const directoryChannels = [
    {
      name: 'Main Community Group',
      role: 'General Fellowship, Announcements & Support',
      tag: 'Primary Group',
      bot: 'Susy Bot',
      link: 'https://t.me/youthopiabiblecommunity',
    },
    {
      name: 'Scripture & Devotional Hub',
      role: 'Daily VOTD & Reflection Studies',
      tag: 'Theo Bot',
      bot: '@iamtheobot',
      link: 'https://t.me/iamtheobot',
    },
    {
      name: 'Prayer & Intercession Line',
      role: 'Prayer Requests & Midweek Sessions',
      tag: 'Eddy Bot',
      bot: '@iamedyybot',
      link: 'https://t.me/iamedyybot',
    },
    {
      name: 'Quiz & Challenge Arena',
      role: 'Daily Bible Trivia & Leaderboards',
      tag: 'Lusy Bot',
      bot: '@iamlusybot',
      link: 'https://t.me/iamlusybot',
    },
    {
      name: 'Security & Moderation Checkpoint',
      role: 'Captcha Verification & Trust Ratings',
      tag: 'Pete Bot',
      bot: '@iampetebot',
      link: 'https://t.me/iampetebot',
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
    <div className="section-stack">
      {/* Susy Hostess Hero Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, #701a75 0%, #a21caf 50%, #e879f9 100%)',
          borderRadius: 'var(--radius-xl)',
          padding: '24px 20px',
          color: '#ffffff',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: 'var(--shadow-lg)',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: -40,
            right: -30,
            width: 140,
            height: 140,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%)',
          }}
        />
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 10 }}>
            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                background: 'rgba(255, 255, 255, 0.2)',
                backdropFilter: 'blur(8px)',
                padding: '4px 10px',
                borderRadius: 999,
              }}
            >
              Hostess & Hospitality Hub
            </span>
            <span style={{ fontSize: 12, opacity: 0.9 }}>• Susy & Pete</span>
          </div>

          <h2 style={{ fontSize: 24, fontWeight: 800, margin: '0 0 8px 0', letterSpacing: '-0.03em', lineHeight: 1.2 }}>
            Welcome to YouThopia Family
          </h2>
          <p style={{ fontSize: 13, lineHeight: 1.6, opacity: 0.92, margin: 0 }}>
            I am Susy, your community hostess and onboarding guide. Explore our fellowship channels, verify your standing with Pete, and find your place in the family!
          </p>
        </div>
      </div>

      {/* Pete Security Checkpoint Card */}
      <Card style={{ padding: 18 }} hover>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 16 }}>🛡️</span>
            <span
              style={{
                fontSize: 12,
                fontWeight: 700,
                color: 'var(--success)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              Pete Security & Trust Checkpoint
            </span>
          </div>
          <Pill color="success">● Account Shielded</Pill>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
          Pete Bot actively protects our fellowship against spam and unauthorized bots. Your account has passed verification with an optimal{' '}
          <strong style={{ color: 'var(--success)' }}>100/100 Trust Score</strong>.
        </p>
      </Card>

      {/* Directory Section */}
      <div>
        <SectionTitle right={<Pill color="purple">5 Bots Active</Pill>}>
          Community Directory & Ecosystem
        </SectionTitle>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
          {directoryChannels.map((chan, idx) => (
            <Card
              key={idx}
              hover
              style={{
                padding: 16,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-color)' }}>{chan.name}</span>
                  <Pill color="purple">{chan.tag}</Pill>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>{chan.role}</div>
              </div>
              <a
                href={chan.link}
                target="_blank"
                rel="noreferrer"
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: 'var(--primary-purple)',
                  textDecoration: 'none',
                  background: 'var(--purple-50)',
                  border: '1px solid var(--purple-100)',
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-md)',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease',
                }}
              >
                Open →
              </a>
            </Card>
          ))}
        </div>
      </div>

      {/* 3-Step Onboarding Guide */}
      <Card style={{ padding: 18 }} hover>
        <SectionTitle right={<Pill color="purple">3 Steps</Pill>}>
          New Member Quick-Start
        </SectionTitle>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginTop: 12 }}>
          {onboardingSteps.map((s) => (
            <div key={s.step} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 800,
                  color: 'var(--primary-purple)',
                  background: 'var(--purple-50)',
                  border: '1px solid var(--purple-100)',
                  padding: '6px 10px',
                  borderRadius: 'var(--radius-md)',
                  flexShrink: 0,
                }}
              >
                {s.step}
              </span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-color)' }}>{s.title}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2, lineHeight: 1.5 }}>
                  {s.description}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Community FAQ Accordion */}
      <Card style={{ padding: 18 }} hover>
        <SectionTitle>Frequently Asked Questions</SectionTitle>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
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
                    maxHeight: isOpen ? 220 : 0,
                    overflow: 'hidden',
                    transition: 'max-height 0.25s var(--ease)',
                  }}
                >
                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, margin: '2px 0 6px 0' }}>
                    {faq.answer}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};
