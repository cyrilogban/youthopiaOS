import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppData } from '../../context/AppData';
import { fetchCommunityStats, type CommunityStats } from '../../services/api';
import { Card, Pill, SectionTitle } from '../../components/ui';
import { COMMUNITY_SPACES } from '../../data/community';

interface SusieHomeProps {
  onOpenTour?: () => void;
}

export const SusieHome: React.FC<SusieHomeProps> = ({ onOpenTour }) => {
  const navigate = useNavigate();
  const { user } = useAppData();
  const [stats, setStats] = useState<CommunityStats | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetchCommunityStats().then((loaded) => {
      if (!cancelled) setStats(loaded);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const name = user?.firstName || 'friend';

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Welcome home, {name}.</h1>
        <p>I'm Susie, your hostess. Let me help you find your way around and feel at home here.</p>
      </section>

      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span className="profile-avatar" style={{ width: 52, height: 52, fontSize: 22 }}>
            💬
          </span>
          <div>
            <strong style={{ fontSize: 15 }}>Susan, your community hostess</strong>
            <p className="muted-copy" style={{ marginTop: 3 }}>Sharing God's Love All The Way</p>
          </div>
        </div>
        <p className="muted-copy" style={{ marginTop: 14 }}>
          New here? Start with the guided tour, then meet the family of assistants who will walk with you
          through Scripture, quizzes, events, and community life.
        </p>
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Start here" right={<Pill color="purple">+50 Trust</Pill>}>The YouThopia Tour</SectionTitle>
        <Card style={{ padding: 16 }}>
          <p className="muted-copy" style={{ margin: 0 }}>
            Five short pages on our mission, vision, and the five pillars. Finishing it marks you oriented and
            claims your one-time welcome boost.
          </p>
          <button className="primary-button" onClick={onOpenTour} style={{ marginTop: 12, width: '100%' }}>
            Start the tour
          </button>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Your path" right={<Pill color="slate">5 steps</Pill>}>Getting started</SectionTitle>
        <Card style={{ padding: 16 }}>
          <div style={{ display: 'grid', gap: 10 }}>
            <button className="secondary-button" onClick={() => navigate('/susie/onboarding')} style={{ width: '100%' }}>
              View the onboarding checklist
            </button>
            <button className="secondary-button" onClick={() => navigate('/susie/directory')} style={{ width: '100%' }}>
              Meet the assistant family
            </button>
          </div>
        </Card>
      </section>

      {stats && (
        <section className="section-group">
          <SectionTitle eyebrow="Our community" right={<Pill color="success">Live</Pill>}>YouThopia today</SectionTitle>
          <div className="metric-grid">
            <div className="metric-tile">
              <div className="metric-label">Members</div>
              <div className="metric-value">{stats.totalMembers.toLocaleString()}</div>
            </div>
            <div className="metric-tile">
              <div className="metric-label">Groups</div>
              <div className="metric-value">{stats.activeGroups.toLocaleString()}</div>
            </div>
            <div className="metric-tile">
              <div className="metric-label">Quizzes</div>
              <div className="metric-value">{stats.quizzesPlayed.toLocaleString()}</div>
            </div>
          </div>
        </section>
      )}

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
