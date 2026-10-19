import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppData } from '../../context/AppData';
import { Card, Pill, ProgressBar, SectionTitle } from '../../components/ui';
import { ONBOARDING_STEPS } from '../../data/community';

interface SusieOnboardingProps {
  onOpenTour?: () => void;
}

export const SusieOnboarding: React.FC<SusieOnboardingProps> = ({ onOpenTour }) => {
  const navigate = useNavigate();
  const { profile } = useAppData();
  const isOriented = profile.status === 'ok' && profile.profile.engagementLevel === 'onboarded';

  const steps = ONBOARDING_STEPS.map((step) => ({
    ...step,
    done: step.step === '02' && isOriented,
  }));
  const doneCount = steps.filter((step) => step.done).length;

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Your start here.</h1>
        <p>A gentle path through everything YouThopia offers. Take it one step at a time.</p>
      </section>

      <Card style={{ padding: 18 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
          <strong style={{ fontSize: 14 }}>Orientation</strong>
          <Pill color={isOriented ? 'success' : 'warning'}>{isOriented ? 'Oriented' : 'Getting started'}</Pill>
        </div>
        <div style={{ marginTop: 14 }}>
          <ProgressBar value={doneCount} max={steps.length} />
          <p className="muted-copy" style={{ marginTop: 8 }}>
            {doneCount} of {steps.length} steps on your welcome path.
          </p>
        </div>
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Step by step" right={<Pill color="slate">{steps.length} steps</Pill>}>The welcome path</SectionTitle>
        <div style={{ display: 'grid', gap: 10 }}>
          {steps.map((step) => (
            <Card key={step.step} style={{ padding: 16 }}>
              <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 800,
                    color: step.done ? '#fff' : 'var(--accent)',
                    background: step.done ? 'var(--accent)' : 'var(--accent-soft)',
                    border: '1px solid var(--accent-soft)',
                    padding: '5px 9px',
                    borderRadius: 'var(--radius-md)',
                    flexShrink: 0,
                  }}
                >
                  {step.done ? '✓' : step.step}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
                    <strong style={{ fontSize: 14 }}>{step.title}</strong>
                    <Pill color="purple">{step.space}</Pill>
                  </div>
                  <p className="muted-copy" style={{ marginTop: 4 }}>{step.description}</p>
                  {step.step === '02' ? (
                    <button className="secondary-button" onClick={onOpenTour} style={{ marginTop: 10 }}>
                      {step.done ? 'Review the tour' : 'Take the tour'}
                    </button>
                  ) : step.route ? (
                    <button className="secondary-button" onClick={() => navigate(step.route!)} style={{ marginTop: 10 }}>
                      Go to {step.space}
                    </button>
                  ) : null}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
};
