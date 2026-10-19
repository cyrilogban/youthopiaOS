import React from 'react';
import { Card, Pill, SectionTitle } from '../../components/ui';
import { GAME_MODES } from '../../data/games';

const lusieLink = (payload: string) => `https://t.me/lusiequizbot?start=${payload}`;

export const LusiePlay: React.FC = () => (
  <div className="section-stack">
    <section className="page-heading">
      <h1>Choose your challenge.</h1>
      <p>Every mode sharpens a different muscle. Pick one, play a quick round, and collect your points.</p>
    </section>

    <section className="section-group">
      <SectionTitle eyebrow="Start here" right={<Pill color="purple">Featured</Pill>}>Today's challenge</SectionTitle>
      <Card style={{ padding: 20, borderColor: 'var(--purple-200)' }}>
        <div className="eyebrow">Bible Challenge</div>
        <h2 style={{ margin: '6px 0 0', fontSize: 21 }}>Five questions. One stronger foundation.</h2>
        <p className="muted-copy" style={{ marginTop: 8 }}>A focused round to test what you know and earn XP for every correct answer.</p>
        <a className="primary-button" href={lusieLink('playquiz')} target="_blank" rel="noreferrer" style={{ marginTop: 16 }}>
          Start challenge
        </a>
      </Card>
    </section>

    <section className="section-group">
      <SectionTitle eyebrow="Play your way" right={<Pill color="slate">{GAME_MODES.length} modes</Pill>}>Game modes</SectionTitle>
      <div style={{ display: 'grid', gap: 10 }}>
        {GAME_MODES.map((game) => (
          <Card key={game.path} style={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
              <div style={{ flex: 1 }}>
                <strong style={{ fontSize: 15 }}>{game.title}</strong>
                <p className="muted-copy" style={{ marginTop: 4 }}>{game.description}</p>
                <Pill color="slate" style={{ marginTop: 10 }}>{game.reward}</Pill>
              </div>
              <a className="secondary-button" href={lusieLink(game.path)} target="_blank" rel="noreferrer" style={{ minHeight: 44, paddingInline: 13 }}>
                Open
              </a>
            </div>
          </Card>
        ))}
      </div>
    </section>

    <Card style={{ padding: 16 }}>
      <SectionTitle eyebrow="Never quiet">Auto quizzes</SectionTitle>
      <p className="muted-copy" style={{ margin: 0 }}>
        Lusie also drops 10 to 15 casual quizzes a day in the community chats, so there is always a chance to play
        and climb. Keep your notifications on and jump in when one appears.
      </p>
    </Card>
  </div>
);
